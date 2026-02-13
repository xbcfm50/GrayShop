from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Apartment(Base):
    __tablename__ = "apartments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    bills: Mapped[list["UtilityBill"]] = relationship(back_populates="apartment")


class UtilityType(Base):
    __tablename__ = "utility_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name_hr: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    bills: Mapped[list["UtilityBill"]] = relationship(back_populates="utility")


class UtilityBill(Base):
    __tablename__ = "utility_bills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    apartment_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("apartments.id"), nullable=True, index=True)
    utility_type: Mapped[str] = mapped_column(String(50), ForeignKey("utility_types.code"), nullable=False, index=True)
    consumption_month: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    received_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    billing_month: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    paid_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    utility: Mapped[UtilityType] = relationship(back_populates="bills")
    apartment: Mapped[Optional[Apartment]] = relationship(back_populates="bills")


class BillingMonth(Base):
    __tablename__ = "billing_months"

    billing_month: Mapped[date] = mapped_column(Date, primary_key=True)
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class Setting(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rent_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    billing_day: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    active_year: Mapped[int] = mapped_column(Integer, default=lambda: date.today().year, nullable=False)
