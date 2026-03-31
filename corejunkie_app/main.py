from datetime import date

from fastapi import APIRouter, Depends, FastAPI, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from corejunkie_app.config import settings
from corejunkie_app.database import Base, engine, get_db
from corejunkie_app.models import InventoryItem, Product, User
from corejunkie_app.runout import estimate_runout_date
from corejunkie_app.schemas import (
    InventoryCreate,
    InventoryOut,
    ProductCreate,
    ProductOut,
    UserCreate,
    UserLogin,
    UserOut,
)
from corejunkie_app.security import COOKIE_NAME, hash_password, make_session_token, parse_session_token, verify_password

app = FastAPI(title="CoreJunkie Product Tracker")
api = APIRouter(prefix=settings.app_base_path)
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


def get_current_user(request: Request, db: Session) -> User | None:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    user_id = parse_session_token(token)
    if not user_id:
        return None
    return db.get(User, user_id)


def require_user(request: Request, db: Session) -> User:
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Login required")
    return user


@app.get("/")
def root():
    return {
        "message": "CoreJunkie tracker API",
        "base_url": settings.app_base_url,
        "base_path": settings.app_base_path,
        "docs": f"{settings.app_base_path}/docs",
    }


@api.get("/", response_class=HTMLResponse)
def app_home(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    return templates.TemplateResponse(
        request,
        "home.html",
        {"base_path": settings.app_base_path, "current_user": current_user},
    )


@api.get("/register", response_class=HTMLResponse)
def register_form(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        request,
        "register.html",
        {"base_path": settings.app_base_path, "current_user": get_current_user(request, db), "error": None},
    )


@api.post("/register")
def register_submit(
    request: Request,
    display_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    if len(password) < 8:
        return templates.TemplateResponse(
            request,
            "register.html",
            {"base_path": settings.app_base_path, "current_user": None, "error": "Password must be 8+ chars."},
            status_code=400,
        )
    if db.scalar(select(User).where(User.email == email)):
        return templates.TemplateResponse(
            request,
            "register.html",
            {"base_path": settings.app_base_path, "current_user": None, "error": "Email already exists."},
            status_code=400,
        )

    user = User(email=email, display_name=display_name, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)

    response = RedirectResponse(url=f"{settings.app_base_path}/dashboard", status_code=303)
    response.set_cookie(COOKIE_NAME, make_session_token(user.id), httponly=True, samesite="lax")
    return response


@api.get("/login", response_class=HTMLResponse)
def login_form(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        request,
        "login.html",
        {"base_path": settings.app_base_path, "current_user": get_current_user(request, db), "error": None},
    )


@api.post("/login")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            request,
            "login.html",
            {"base_path": settings.app_base_path, "current_user": None, "error": "Invalid credentials."},
            status_code=401,
        )

    response = RedirectResponse(url=f"{settings.app_base_path}/dashboard", status_code=303)
    response.set_cookie(COOKIE_NAME, make_session_token(user.id), httponly=True, samesite="lax")
    return response


@api.post("/logout")
def logout():
    response = RedirectResponse(url=f"{settings.app_base_path}/login", status_code=303)
    response.delete_cookie(COOKIE_NAME)
    return response


@api.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    rows = (
        db.scalars(
            select(InventoryItem)
            .where(InventoryItem.user_id == user.id)
            .options(joinedload(InventoryItem.product))
            .order_by(InventoryItem.created_at.desc())
        )
        .unique()
        .all()
    )
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {"base_path": settings.app_base_path, "current_user": user, "rows": rows},
    )


@api.get("/products/new", response_class=HTMLResponse)
def new_product_form(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    return templates.TemplateResponse(
        request,
        "new_product.html",
        {"base_path": settings.app_base_path, "current_user": user, "error": None},
    )


@api.post("/products/new")
def new_product_submit(
    request: Request,
    name: str = Form(...),
    category: str = Form(...),
    size_value: float = Form(...),
    size_unit: str = Form("fl_oz"),
    db: Session = Depends(get_db),
):
    user = require_user(request, db)
    if size_value <= 0:
        return templates.TemplateResponse(
            request,
            "new_product.html",
            {"base_path": settings.app_base_path, "current_user": user, "error": "Size must be > 0."},
            status_code=400,
        )
    db.add(Product(name=name, category=category, size_value=size_value, size_unit=size_unit))
    db.commit()
    return RedirectResponse(url=f"{settings.app_base_path}/dashboard", status_code=303)


@api.get("/inventory/new", response_class=HTMLResponse)
def new_inventory_form(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    products = list(db.scalars(select(Product).order_by(Product.name.asc())).all())
    return templates.TemplateResponse(
        request,
        "new_inventory.html",
        {"base_path": settings.app_base_path, "current_user": user, "products": products, "error": None},
    )


@api.post("/inventory/new")
def new_inventory_submit(
    request: Request,
    product_id: int = Form(...),
    purchased_at: date = Form(...),
    opened_at: date | None = Form(None),
    cadence_value: float | None = Form(None),
    cadence_unit: str | None = Form(None),
    amount_per_use: float | None = Form(None),
    db: Session = Depends(get_db),
):
    user = require_user(request, db)
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    expected_run_out_at = None
    if opened_at and cadence_value and cadence_unit and amount_per_use:
        expected_run_out_at = estimate_runout_date(product.size_value, opened_at, cadence_value, cadence_unit, amount_per_use)

    db.add(
        InventoryItem(
            user_id=user.id,
            product_id=product_id,
            purchased_at=purchased_at,
            opened_at=opened_at,
            cadence_value=cadence_value,
            cadence_unit=cadence_unit,
            amount_per_use=amount_per_use,
            expected_run_out_at=expected_run_out_at,
        )
    )
    db.commit()
    return RedirectResponse(url=f"{settings.app_base_path}/dashboard", status_code=303)


# JSON API endpoints
@api.post("/users", response_model=UserOut)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        return existing
    user = User(email=payload.email, display_name=payload.display_name, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@api.post("/auth/login")
def login_api(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": make_session_token(user.id), "user_id": user.id}


@api.get("/me", response_model=UserOut)
def me(request: Request, db: Session = Depends(get_db)):
    user = require_user(request, db)
    return user


@api.post("/products", response_model=ProductOut)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@api.get("/products", response_model=list[ProductOut])
def list_products(
    q: str | None = Query(default=None),
    category: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(Product)
    if q:
        stmt = stmt.where(Product.name.ilike(f"%{q}%"))
    if category:
        stmt = stmt.where(Product.category == category)
    return list(db.scalars(stmt.order_by(Product.name.asc())).all())


@api.post("/inventory", response_model=InventoryOut)
def add_inventory_item(payload: InventoryCreate, db: Session = Depends(get_db)):
    user = db.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    product = db.get(Product, payload.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    expected_run_out_at = None
    if payload.opened_at and payload.cadence_value and payload.cadence_unit and payload.amount_per_use:
        expected_run_out_at = estimate_runout_date(
            package_size=product.size_value,
            opened_at=payload.opened_at,
            cadence_value=payload.cadence_value,
            cadence_unit=payload.cadence_unit,
            amount_per_use=payload.amount_per_use,
        )

    record = InventoryItem(**payload.model_dump(), expected_run_out_at=expected_run_out_at)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@api.get("/users/{user_id}/inventory", response_model=list[InventoryOut])
def list_user_inventory(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    stmt = select(InventoryItem).where(InventoryItem.user_id == user_id).order_by(InventoryItem.created_at.desc())
    return list(db.scalars(stmt).all())


app.include_router(api)
