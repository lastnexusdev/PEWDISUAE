from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from corejunkie_app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    inventory_items: Mapped[list["InventoryItem"]] = relationship(back_populates="user")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    size_value: Mapped[float] = mapped_column(Float, nullable=False)
    size_unit: Mapped[str] = mapped_column(String(20), nullable=False, default="fl_oz")

    inventory_items: Mapped[list["InventoryItem"]] = relationship(back_populates="product")


class InventoryItem(Base):
    __tablename__ = "inventory_items"
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", "purchased_at", name="uq_inventory_purchase"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)

    purchased_at: Mapped[date] = mapped_column(Date, nullable=False)
    opened_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    cadence_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    cadence_unit: Mapped[str | None] = mapped_column(String(10), nullable=True)  # day/week
    amount_per_use: Mapped[float | None] = mapped_column(Float, nullable=True)

    expected_run_out_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="inventory_items")
    product: Mapped[Product] = relationship(back_populates="inventory_items")
