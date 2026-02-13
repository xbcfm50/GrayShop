from __future__ import annotations

import os
import shutil
import sys
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import Select, case, func, select
from sqlalchemy.orm import Session, joinedload

from app.db import DB_PATH, Base, engine
from app.models import BillingMonth, Setting, UtilityBill, UtilityType

HR_MONTHS = [
    "siječanj",
    "veljača",
    "ožujak",
    "travanj",
    "svibanj",
    "lipanj",
    "srpanj",
    "kolovoz",
    "rujan",
    "listopad",
    "studeni",
    "prosinac",
]


@dataclass
class ExpectedRow:
    utility_type: str
    utility_name: str
    consumption_month: date
    received: bool
    first_received_date: date | None
    charged: bool


def first_of_month(value: date) -> date:
    return value.replace(day=1)


def next_month(value: date) -> date:
    if value.month == 12:
        return date(value.year + 1, 1, 1)
    return date(value.year, value.month + 1, 1)


def prev_month(value: date) -> date:
    if value.month == 1:
        return date(value.year - 1, 12, 1)
    return date(value.year, value.month - 1, 1)


def month_label_hr(value: date) -> str:
    return f"{HR_MONTHS[value.month - 1]}-{value.year}"


def format_date_hr(value: date | None) -> str:
    if not value:
        return ""
    return value.strftime("%d.%m.%Y")


def format_money_hr(value: Decimal | None) -> str:
    if value is None:
        return "0,00"
    return f"{value:.2f}".replace(".", ",")


def compute_billing_month(received_date: date, billing_day: int) -> date:
    month = first_of_month(received_date)
    if received_date.day <= billing_day:
        return month
    return next_month(month)


def current_billing_month(today: date, billing_day: int) -> date:
    month = first_of_month(today)
    if today.day <= billing_day:
        return month
    return next_month(month)


def init_db(session: Session) -> None:
    Base.metadata.create_all(bind=engine)
    has_settings = session.scalar(select(func.count()).select_from(Setting))
    if not has_settings:
        session.add(Setting(rent_amount=Decimal("0.00"), billing_day=10, active_year=date.today().year))
    for code, name in [
        ("electricity", "Električna energija"),
        ("water", "Voda"),
        ("gas", "Plin"),
        ("waste", "Odvoz otpada"),
    ]:
        exists = session.scalar(select(func.count()).select_from(UtilityType).where(UtilityType.code == code))
        if not exists:
            session.add(UtilityType(code=code, name_hr=name, is_active=True))
    session.commit()


def get_settings(session: Session) -> Setting:
    settings = session.scalar(select(Setting).limit(1))
    assert settings is not None
    return settings


def validate_month_first(value: date) -> bool:
    return value.day == 1


def ensure_billing_month(session: Session, month: date) -> BillingMonth:
    billing = session.get(BillingMonth, month)
    if billing is None:
        billing = BillingMonth(billing_month=month, is_closed=False)
        session.add(billing)
        session.flush()
    return billing


def bills_query() -> Select[tuple[UtilityBill]]:
    return select(UtilityBill).options(joinedload(UtilityBill.utility)).order_by(UtilityBill.received_date.desc(), UtilityBill.id.desc())


def expected_rows(session: Session, year: int) -> list[ExpectedRow]:
    active_types = session.scalars(select(UtilityType).where(UtilityType.is_active.is_(True)).order_by(UtilityType.name_hr)).all()
    results: list[ExpectedRow] = []
    for utility in active_types:
        for month in range(1, 13):
            consumption = date(year, month, 1)
            stats = session.execute(
                select(
                    func.count(UtilityBill.id),
                    func.min(UtilityBill.received_date),
                    func.sum(case((UtilityBill.is_paid.is_(True), 1), else_=0)),
                )
                .where(UtilityBill.utility_type == utility.code)
                .where(UtilityBill.consumption_month == consumption)
            ).one()
            received_count, first_received, charged_count = stats
            results.append(
                ExpectedRow(
                    utility_type=utility.code,
                    utility_name=utility.name_hr,
                    consumption_month=consumption,
                    received=bool(received_count),
                    first_received_date=first_received,
                    charged=bool(charged_count),
                )
            )
    return results


def close_billing_month(session: Session, month: date) -> None:
    with session.begin_nested():
        billing = ensure_billing_month(session, month)
        billing.is_closed = True
        billing.closed_at = datetime.utcnow()
        today = date.today()
        bills = session.scalars(select(UtilityBill).where(UtilityBill.billing_month == month)).all()
        for bill in bills:
            bill.is_paid = True
            bill.paid_date = today


def reopen_billing_month(session: Session, month: date) -> None:
    with session.begin_nested():
        billing = ensure_billing_month(session, month)
        billing.is_closed = False
        billing.closed_at = None
        bills = session.scalars(select(UtilityBill).where(UtilityBill.billing_month == month)).all()
        for bill in bills:
            bill.is_paid = False
            bill.paid_date = None


def import_database(upload_path: Path) -> tuple[bool, str]:
    try:
        shutil.copyfile(upload_path, DB_PATH)
        os.execv(sys.executable, [sys.executable, "main.py"])
    except Exception as exc:  # noqa: BLE001
        return False, f"Baza je uvezena, ali automatski restart nije uspio: {exc}"
    return True, "Aplikacija se ponovno pokreće..."
