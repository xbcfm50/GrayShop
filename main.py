from __future__ import annotations

import shutil
import sys
import tempfile
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import __version__ as PYDANTIC_VERSION

if sys.version_info < (3, 9):
    raise RuntimeError("Potreban je Python 3.9+ za pokretanje aplikacije. Preporučeno: Python 3.11.")

if int(PYDANTIC_VERSION.split(".", maxsplit=1)[0]) < 2:
    raise RuntimeError(
        "Potrebna je pydantic>=2. Instalirajte ovisnosti iz requirements.txt (npr. `python -m pip install -r requirements.txt`)."
    )

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import DB_PATH, SessionLocal, get_session
from app.models import Apartment, BillingMonth, UtilityBill, UtilityType
from app.services import (
    HR_MONTHS,
    close_billing_month,
    compute_billing_month,
    current_billing_month,
    expected_rows,
    format_date_hr,
    format_money_hr,
    get_settings,
    import_database,
    init_db,
    month_label_hr,
    prev_month,
    reopen_billing_month,
    validate_month_first,
)

app = FastAPI(title="Evidencija računa")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
def startup() -> None:
    with SessionLocal() as session:
        init_db(session)


def ctx(request: Request, **kwargs):
    base = {
        "request": request,
        "format_date_hr": format_date_hr,
        "format_money_hr": format_money_hr,
        "month_label_hr": month_label_hr,
    }
    base.update(kwargs)
    return base


def parse_date(raw: str, field: str) -> date:
    candidates = [
        ("%Y-%m", lambda d: date(d.year, d.month, 1)),
        ("%Y-%m-%d", lambda d: date(d.year, d.month, 1)),
        ("%m/%Y", lambda d: date(d.year, d.month, 1)),
        ("%m-%Y", lambda d: date(d.year, d.month, 1)),
        ("%m.%Y", lambda d: date(d.year, d.month, 1)),
    ]
    for pattern, normalize in candidates:
        try:
            return normalize(datetime.strptime(raw, pattern).date())
        except ValueError:
            pass
    raise HTTPException(status_code=400, detail=f"Neispravan mjesec za {field}.")


def month_choice_label(month_number: int) -> str:
    return HR_MONTHS[month_number - 1].capitalize()


def month_select_options() -> List[Dict[str, Union[str, int]]]:
    return [{"value": month, "label": month_choice_label(month)} for month in range(1, 13)]


def year_select_options(active_year: int) -> list[int]:
    return [active_year - 1, active_year, active_year + 1]


def parse_consumption_month(month_value: str, year_value: str, fallback_raw: str, field: str) -> date:
    if month_value and year_value:
        try:
            month_int = int(month_value)
            year_int = int(year_value)
            return date(year_int, month_int, 1)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=f"Neispravan mjesec za {field}.") from exc
    return parse_month(fallback_raw, field)


    apartment_map = {a.id: a.name for a in session.scalars(select(Apartment)).all()}
    return templates.TemplateResponse(
        "bills_list.html",
        ctx(request, bills=bills, utility_map=utility_map, apartment_map=apartment_map, closed_months=closed_months),
    )
    settings = get_settings(session)
    apartments = session.scalars(select(Apartment).where(Apartment.is_active.is_(True)).order_by(Apartment.name)).all()
    return templates.TemplateResponse(
        "bill_form.html",
        ctx(
            request,
            bill=None,
            utility_types=utility_types,
            apartments=apartments,
            month_options=month_select_options(),
            year_options=year_select_options(settings.active_year),
            settings=settings,
            error=None,
        ),
    )
    settings = get_settings(session)
    apartments = session.scalars(select(Apartment).order_by(Apartment.name)).all()
    return templates.TemplateResponse(
        "bill_form.html",
        ctx(
            request,
            bill=bill,
            utility_types=utility_types,
            apartments=apartments,
            month_options=month_select_options(),
            year_options=year_select_options(settings.active_year),
            settings=settings,
            error=None,
        ),
    )
    apartment_id: int | None,
    consumption_month_month: str,
    consumption_month_year: str,
        "apartment_id": apartment_id,
        "consumption_month_month": consumption_month_month,
        "consumption_month_year": consumption_month_year,
    apartment_id: int = Form(...),
    consumption_month: str = Form(default=""),
    consumption_month_month: str = Form(default=""),
    consumption_month_year: str = Form(default=""),
    apartments = session.scalars(select(Apartment).where(Apartment.is_active.is_(True)).order_by(Apartment.name)).all()
    active_apartment_ids = {item.id for item in apartments}
    form_bill = build_bill_form_data(
        bill_id,
        apartment_id,
        utility_type,
        consumption_month,
        consumption_month_month,
        consumption_month_year,
        received_date,
        amount,
        note,
    )

    if apartment_id not in active_apartment_ids:
        return templates.TemplateResponse(
            "bill_form.html",
            ctx(
                request,
                bill=form_bill,
                utility_types=utility_types,
                apartments=apartments,
                month_options=month_select_options(),
                year_options=year_select_options(settings.active_year),
                settings=settings,
                error="Odabrani stan nije valjan ili više nije aktivan.",
            ),
            status_code=400,
    bill_id: Optional[int],
    apartment_id: Optional[int],
    bill_id: Optional[int] = Form(default=None),
                apartments=apartments,
                month_options=month_select_options(),
                year_options=year_select_options(settings.active_year),
        consumption = parse_consumption_month(consumption_month_month, consumption_month_year, consumption_month, "mjesec potrošnje")
                bill=form_bill,
                apartments=apartments,
                month_options=month_select_options(),
                year_options=year_select_options(settings.active_year),
                bill=form_bill,
                apartments=apartments,
                month_options=month_select_options(),
                year_options=year_select_options(settings.active_year),
                bill=form_bill,
                apartments=apartments,
                month_options=month_select_options(),
                year_options=year_select_options(settings.active_year),
                bill=form_bill,
                apartments=apartments,
                month_options=month_select_options(),
                year_options=year_select_options(settings.active_year),
                bill=form_bill,
                apartments=apartments,
                month_options=month_select_options(),
                year_options=year_select_options(settings.active_year),
    bill.apartment_id = apartment_id
    apartment_map = {a.id: a.name for a in session.scalars(select(Apartment)).all()}
            apartment_map=apartment_map,
    apartments = session.scalars(select(Apartment).order_by(Apartment.name)).all()
    return templates.TemplateResponse("settings.html", ctx(request, settings=settings, utility_types=types, apartments=apartments, error=None))
    apartments = session.scalars(select(Apartment).order_by(Apartment.name)).all()
        return templates.TemplateResponse("settings.html", ctx(request, settings=settings, utility_types=types, apartments=apartments, error="Neispravan iznos najamnine."), status_code=400)
        return templates.TemplateResponse("settings.html", ctx(request, settings=settings, utility_types=types, apartments=apartments, error="Dan obračuna mora biti između 1 i 28."), status_code=400)
@app.post("/settings/apartment/add")
def apartment_add(name: str = Form(...), session: Session = Depends(get_session)):
    apartment_name = name.strip()
    if not apartment_name:
        raise HTTPException(status_code=400, detail="Naziv stana je obavezan.")
    exists = session.scalar(select(func.count()).select_from(Apartment).where(Apartment.name == apartment_name))
    if exists:
        raise HTTPException(status_code=400, detail="Stan s tim nazivom već postoji.")
    session.add(Apartment(name=apartment_name, is_active=True))
    session.commit()
    return RedirectResponse(url="/settings", status_code=303)


@app.post("/settings/apartment/{apartment_id}/deactivate")
def apartment_deactivate(apartment_id: int, session: Session = Depends(get_session)):
    apartment = session.get(Apartment, apartment_id)
    if not apartment:
        raise HTTPException(status_code=404, detail="Stan nije pronađen.")
    active_count = session.scalar(select(func.count()).select_from(Apartment).where(Apartment.is_active.is_(True)))
    if apartment.is_active and active_count <= 1:
        raise HTTPException(status_code=400, detail="Mora postojati barem jedan aktivan stan.")
    apartment.is_active = False
    session.commit()
    return RedirectResponse(url="/settings", status_code=303)


    apartments = session.scalars(select(Apartment).order_by(Apartment.name)).all()
    return templates.TemplateResponse("settings.html", ctx(request, settings=get_settings(session), utility_types=types, apartments=apartments, error=message if not ok else None))
    late_unreceived = [r for r in expected_rows(session, settings.active_year) if not r.received]
    return templates.TemplateResponse(
        "dashboard.html",
        ctx(
            request,
            settings=settings,
            current_billing_month=curr,
            rent_display_month=prev_month(curr),
            bills_in_curr=bills_in_curr,
            is_current_closed=bool(closed_curr),
            missing_count=len(late_unreceived),
        ),
    )


@app.get("/bills")
def bills_list(request: Request, session: Session = Depends(get_session)):
    bills = session.scalars(select(UtilityBill).order_by(UtilityBill.received_date.desc(), UtilityBill.id.desc())).all()
    utility_map = {u.code: u.name_hr for u in session.scalars(select(UtilityType)).all()}
    closed_months = {m.billing_month for m in session.scalars(select(BillingMonth).where(BillingMonth.is_closed.is_(True))).all()}
    return templates.TemplateResponse("bills_list.html", ctx(request, bills=bills, utility_map=utility_map, closed_months=closed_months))


@app.get("/bills/new")
def bill_new(request: Request, session: Session = Depends(get_session)):
    utility_types = session.scalars(select(UtilityType).where(UtilityType.is_active.is_(True)).order_by(UtilityType.name_hr)).all()
    return templates.TemplateResponse("bill_form.html", ctx(request, bill=None, utility_types=utility_types, settings=get_settings(session), error=None))


@app.get("/bills/{bill_id}/edit")
def bill_edit(bill_id: int, request: Request, session: Session = Depends(get_session)):
    bill = session.get(UtilityBill, bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Račun nije pronađen.")
    utility_types = session.scalars(select(UtilityType).where(UtilityType.is_active.is_(True)).order_by(UtilityType.name_hr)).all()
    return templates.TemplateResponse("bill_form.html", ctx(request, bill=bill, utility_types=utility_types, settings=get_settings(session), error=None))


def build_bill_form_data(
    bill_id: int | None,
    utility_type: str,
    consumption_month: str,
    received_date: str,
    amount: str,
    note: str,
):
    return {
        "id": bill_id,
        "utility_type": utility_type,
        "consumption_month": consumption_month,
        "received_date": received_date,
        "amount": amount,
        "note": note,
    }


@app.post("/bills/save")
def bill_save(
    request: Request,
    bill_id: int | None = Form(default=None),
    utility_type: str = Form(...),
    consumption_month: str = Form(...),
    received_date: str = Form(...),
    amount: str = Form(...),
    note: str = Form(default=""),
    session: Session = Depends(get_session),
):
    settings = get_settings(session)
    utility_types = session.scalars(select(UtilityType).where(UtilityType.is_active.is_(True)).order_by(UtilityType.name_hr)).all()
    active_codes = {item.code for item in utility_types}
    if utility_type not in active_codes:
        return templates.TemplateResponse(
            "bill_form.html",
            ctx(
                request,
                bill=build_bill_form_data(bill_id, utility_type, consumption_month, received_date, amount, note),
                utility_types=utility_types,
                settings=settings,
                error="Odabrani tip režije nije valjan ili više nije aktivan.",
            ),
            status_code=400,
        )
    try:
        consumption = parse_month(consumption_month, "mjesec potrošnje")
        received = parse_date(received_date, "datum primitka")
            ctx(
                request,
                bill=build_bill_form_data(bill_id, utility_type, consumption_month, received_date, amount, note),
                utility_types=utility_types,
                settings=settings,
                error=exc.detail,
            ),
        return templates.TemplateResponse(
            "bill_form.html",
            ctx(
                request,
                bill=build_bill_form_data(bill_id, utility_type, consumption_month, received_date, amount, note),
                utility_types=utility_types,
                settings=settings,
                error="Mjesec potrošnje mora biti prvi dan mjeseca.",
            ),
            status_code=400,
        )
        return templates.TemplateResponse(
            "bill_form.html",
            ctx(
                request,
                bill=build_bill_form_data(bill_id, utility_type, consumption_month, received_date, amount, note),
                utility_types=utility_types,
                settings=settings,
                error="Datum primitka ne smije biti u budućnosti.",
            ),
            status_code=400,
        )
        return templates.TemplateResponse(
            "bill_form.html",
            ctx(
                request,
                bill=build_bill_form_data(bill_id, utility_type, consumption_month, received_date, amount, note),
                utility_types=utility_types,
                settings=settings,
                error="Iznos mora biti pozitivan.",
            ),
            status_code=400,
        )
    month_status = session.get(BillingMonth, billing_month)
    if month_status and month_status.is_closed and bill_id is None:
        return templates.TemplateResponse(
            "bill_form.html",
            ctx(
                request,
                bill=build_bill_form_data(bill_id, utility_type, consumption_month, received_date, amount, note),
                utility_types=utility_types,
                settings=settings,
                error="Obračunski mjesec je zatvoren. Prvo ga ponovno otvorite.",
            ),
            status_code=400,
        )

    if bill_id:
        bill = session.get(UtilityBill, bill_id)
        if not bill:
            raise HTTPException(status_code=404, detail="Račun nije pronađen.")
        existing_month = session.get(BillingMonth, bill.billing_month)
        if existing_month and existing_month.is_closed:
            raise HTTPException(status_code=400, detail="Račun iz zatvorenog mjeseca nije moguće mijenjati.")
        if month_status and month_status.is_closed and bill.billing_month != billing_month:
            raise HTTPException(status_code=400, detail="Ciljani obračunski mjesec je zatvoren.")
    else:
        bill = UtilityBill(created_at=datetime.utcnow())
        session.add(bill)

    bill.utility_type = utility_type
    bill.consumption_month = consumption
    bill.received_date = received
    bill.amount = amount_decimal.quantize(Decimal("0.01"))
    bill.billing_month = billing_month
    bill.note = note or None
    bill.is_paid = False
    bill.paid_date = None

    session.commit()
    return RedirectResponse(url="/bills", status_code=303)


@app.post("/bills/{bill_id}/delete")
def bill_delete(bill_id: int, session: Session = Depends(get_session)):
    bill = session.get(UtilityBill, bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Račun nije pronađen.")
    status = session.get(BillingMonth, bill.billing_month)
    if status and status.is_closed:
        raise HTTPException(status_code=400, detail="Račun iz zatvorenog mjeseca nije moguće obrisati.")
    session.delete(bill)
    session.commit()
    return RedirectResponse(url="/bills", status_code=303)


@app.get("/monthly-charges")
def monthly_charges(request: Request, session: Session = Depends(get_session)):
    months_from_bills = {m for (m,) in session.execute(select(UtilityBill.billing_month).distinct()).all()}
    months_from_status = {m.billing_month: m for m in session.scalars(select(BillingMonth)).all()}
    all_months = sorted(months_from_bills.union(months_from_status.keys()), reverse=True)
    months = [months_from_status.get(month, BillingMonth(billing_month=month, is_closed=False, closed_at=None)) for month in all_months]
    return templates.TemplateResponse("monthly_charges.html", ctx(request, months=months))


@app.get("/monthly-charges/{month}")
def monthly_charge_detail(month: str, request: Request, session: Session = Depends(get_session)):
    billing_month = parse_date(month, "obračunski mjesec")
    settings = get_settings(session)
    bills = session.scalars(select(UtilityBill).where(UtilityBill.billing_month == billing_month).order_by(UtilityBill.utility_type)).all()
    utility_map = {u.code: u.name_hr for u in session.scalars(select(UtilityType)).all()}
    total_utility = sum((b.amount for b in bills), Decimal("0.00"))
    grand_total = total_utility + settings.rent_amount
    month_record = session.get(BillingMonth, billing_month)
    return templates.TemplateResponse(
        "monthly_charge_detail.html",
        ctx(
            request,
            billing_month=billing_month,
            rent_month=prev_month(billing_month),
            bills=bills,
            utility_map=utility_map,
            total_utility=total_utility,
            rent_amount=settings.rent_amount,
            grand_total=grand_total,
            month_record=month_record,
        ),
    )


@app.post("/monthly-charges/{month}/close")
def close_month(month: str, session: Session = Depends(get_session)):
    billing_month = parse_date(month, "obračunski mjesec")
    close_billing_month(session, billing_month)
    session.commit()
    return RedirectResponse(url=f"/monthly-charges/{month}", status_code=303)


@app.post("/monthly-charges/{month}/reopen")
def reopen_month(month: str, session: Session = Depends(get_session)):
    billing_month = parse_date(month, "obračunski mjesec")
    reopen_billing_month(session, billing_month)
    session.commit()
    return RedirectResponse(url=f"/monthly-charges/{month}", status_code=303)


@app.get("/expected-bills")
def expected_bills_page(request: Request, session: Session = Depends(get_session)):
    settings = get_settings(session)
    rows = expected_rows(session, settings.active_year)
    return templates.TemplateResponse("expected_bills.html", ctx(request, rows=rows, year=settings.active_year))


@app.get("/settings")
def settings_page(request: Request, session: Session = Depends(get_session)):
    settings = get_settings(session)
    types = session.scalars(select(UtilityType).order_by(UtilityType.name_hr)).all()
    return templates.TemplateResponse("settings.html", ctx(request, settings=settings, utility_types=types, error=None))


@app.post("/settings/save")
def settings_save(
    request: Request,
    rent_amount: str = Form(...),
    billing_day: int = Form(...),
    active_year: int = Form(...),
    session: Session = Depends(get_session),
):
    settings = get_settings(session)
    types = session.scalars(select(UtilityType).order_by(UtilityType.name_hr)).all()
    try:
        rent = Decimal(rent_amount)
    except InvalidOperation:
        return templates.TemplateResponse("settings.html", ctx(request, settings=settings, utility_types=types, error="Neispravan iznos najamnine."), status_code=400)
    if billing_day < 1 or billing_day > 28:
        return templates.TemplateResponse("settings.html", ctx(request, settings=settings, utility_types=types, error="Dan obračuna mora biti između 1 i 28."), status_code=400)

    settings.rent_amount = rent.quantize(Decimal("0.01"))
    settings.billing_day = billing_day
    settings.active_year = active_year
    session.commit()
    return RedirectResponse(url="/settings", status_code=303)


@app.post("/settings/utility-type/add")
def utility_type_add(code: str = Form(...), name_hr: str = Form(...), session: Session = Depends(get_session)):
    safe_code = code.strip().lower().replace(" ", "_")
    exists = session.scalar(select(func.count()).select_from(UtilityType).where(UtilityType.code == safe_code))
    if exists:
        raise HTTPException(status_code=400, detail="Šifra već postoji.")
    session.add(UtilityType(code=safe_code, name_hr=name_hr.strip(), is_active=True))
    session.commit()
    return RedirectResponse(url="/settings", status_code=303)


@app.post("/settings/utility-type/{type_id}/deactivate")
def utility_type_deactivate(type_id: int, session: Session = Depends(get_session)):
    utility_type = session.get(UtilityType, type_id)
    if not utility_type:
        raise HTTPException(status_code=404, detail="Tip nije pronađen.")
    utility_type.is_active = False
    session.commit()
    return RedirectResponse(url="/settings", status_code=303)


@app.get("/backup/export")
def backup_export():
    return FileResponse(DB_PATH, media_type="application/x-sqlite3", filename="data.db")


@app.post("/backup/import")
def backup_import(request: Request, db_file: UploadFile = File(...), session: Session = Depends(get_session)):
    temp_dir = Path(tempfile.mkdtemp())
    temp_file = temp_dir / "uploaded.db"
    with temp_file.open("wb") as f:
        shutil.copyfileobj(db_file.file, f)
    ok, message = import_database(temp_file)
    types = session.scalars(select(UtilityType).order_by(UtilityType.name_hr)).all()
    return templates.TemplateResponse("settings.html", ctx(request, settings=get_settings(session), utility_types=types, error=message if not ok else None))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
