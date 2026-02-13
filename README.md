# Lokalna evidencija najamnine i režija

Offline aplikacija (FastAPI + SQLite) za praćenje računa, mjesečnih obračuna, očekivanih računa i postavki.

## Pokretanje

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Aplikacija je dostupna na `http://127.0.0.1:8000`.
Svi podaci se spremaju u `data.db`.

## Funkcionalnosti

- Nadzorna ploča s trenutnim obračunskim mjesecom.
- Unos/izmjena/brisanje računa (brisanje je blokirano za zatvorene mjesece).
- Izračun obračunskog mjeseca prema `billing_day`.
- Zatvaranje/ponovno otvaranje mjeseca transakcijski (zatvaranje označava račune kao plaćene).
- Mjesečni obračuni s najamninom i režijama.
- Mreža očekivanih računa za aktivnu godinu.
- Postavke (najamnina, dan obračuna, aktivna godina) + upravljanje tipovima režija.
- Export/import `data.db` (import pokušava automatski restart aplikacije).

## Napomena o proširenju

Model `utility_bills` ima pripremljenu točku proširenja za budući `apartment_id` bez implementacije multi-stan ponašanja u v1.
