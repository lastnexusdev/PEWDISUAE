from datetime import date
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    email: str
    display_name: str
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    display_name: str

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str
    category: str
    size_value: float = Field(gt=0)
    size_unit: str = "fl_oz"


class ProductOut(BaseModel):
    id: int
    name: str
    category: str
    size_value: float
    size_unit: str

    class Config:
        from_attributes = True


class InventoryCreate(BaseModel):
    user_id: int
    product_id: int
    purchased_at: date
    opened_at: date | None = None
    cadence_value: float | None = Field(default=None, gt=0)
    cadence_unit: str | None = None
    amount_per_use: float | None = Field(default=None, gt=0)


class InventoryOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    purchased_at: date
    opened_at: date | None
    cadence_value: float | None
    cadence_unit: str | None
    amount_per_use: float | None
    expected_run_out_at: date | None

    class Config:
        from_attributes = True
