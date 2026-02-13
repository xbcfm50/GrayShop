# Lokalna evidencija najamnine i režija

Offline aplikacija (FastAPI + SQLite) za praćenje računa, mjesečnih obračuna, očekivanih računa i postavki.

## Pokretanje

### Linux / macOS
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

### Windows PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Aplikacija je dostupna na `http://127.0.0.1:8000`.
Svi podaci se spremaju u `data.db`.

## Funkcionalnosti

- Nadzorna ploča s trenutnim obračunskim mjesecom.
- Unos/izmjena/brisanje računa (brisanje je blokirano za zatvorene mjesece).
- Unos mjeseca potrošnje kroz jednostavne padajuće izbornike (mjesec + godina).
- Podrška za više stanova (dodavanje i deaktivacija stanova u postavkama).
- Izračun obračunskog mjeseca prema `billing_day`.
- Zatvaranje/ponovno otvaranje mjeseca transakcijski (zatvaranje označava račune kao plaćene).
- Mjesečni obračuni s najamninom i režijama.
- Mreža očekivanih računa za aktivnu godinu.
- Postavke (najamnina, dan obračuna, aktivna godina) + upravljanje tipovima režija.
- Export/import `data.db` (import pokušava automatski restart aplikacije).

## Napomena o proširenju

Model `utility_bills` ima pripremljenu točku proširenja za budući `apartment_id` bez implementacije multi-stan ponašanja u v1.

## Rješavanje problema

- Ako dobijete grešku tipa `ValueError: 'not' is not a valid parameter name`, vjerojatno je instaliran stari `pydantic` (v1). Pokrenite:

```bash
python -m pip install --upgrade "pydantic>=2.10,<3"
python -m pip install -r requirements.txt
```


- Ako dobijete `SyntaxError: invalid syntax` na anotacijama tipova, provjerite verziju: `python --version`. Preporučeno je Python 3.11+ i pokretanje s tom verzijom (npr. `py -3.11 -m venv .venv` na Windowsu).

- Ako i dalje vidite grešku `SyntaxError: invalid syntax` na liniji s `apartment_id: int | None`, onda pokrećete stariju verziju koda. Povucite zadnje promjene i napravite novi virtualni env:

```powershell
git pull
Remove-Item -Recurse -Force .venv
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```
