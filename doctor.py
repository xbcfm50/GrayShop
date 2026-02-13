from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    print("== GrayShop dijagnostika ==")
    print(f"Python: {sys.version.split()[0]}")

    if sys.version_info < (3, 9):
        print("[GREŠKA] Potreban je Python 3.9+ (preporuka 3.11).")
        return 1

    main_path = Path("main.py")
    if not main_path.exists():
        print("[GREŠKA] main.py nije pronađen u trenutnoj mapi.")
        return 1

    content = main_path.read_text(encoding="utf-8", errors="replace")

    if re.search(r"\b\w+\s*\|\s*None\b", content):
        print("[GREŠKA] Ova kopija main.py još sadrži staru anotaciju tipa `x | None`.")
        print("         To znači da nije povučena zadnja verzija projekta.")
        print("         Rješenje: git pull, pa ponovno kreirati .venv i instalirati requirements.")
        return 1

    print("[OK] main.py ne sadrži zastarjele `x | None` anotacije.")

    try:
        import pydantic  # noqa: PLC0415

        major = int(pydantic.__version__.split(".", maxsplit=1)[0])
        if major < 2:
            print(f"[GREŠKA] pydantic={pydantic.__version__}, potrebno je >=2")
            return 1
        print(f"[OK] pydantic={pydantic.__version__}")
    except Exception as exc:  # noqa: BLE001
        print(f"[UPOZORENJE] pydantic nije dostupan ili nije moguće učitati: {exc}")

    print("[OK] Osnovna dijagnostika je prošla.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
