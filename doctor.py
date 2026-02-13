from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def _ensure_optional_import(content: str) -> str:
    if re.search(r"from typing import .*\bOptional\b", content):
        return content
    if "from typing import" in content:
        return re.sub(r"from typing import ([^\n]+)", lambda m: f"from typing import {m.group(1)}, Optional", content, count=1)
    return content.replace("from pathlib import Path\n", "from pathlib import Path\nfrom typing import Optional\n", 1)


def _rewrite_legacy_unions(content: str) -> tuple[str, int]:
    pattern = re.compile(r"\b([A-Za-z_][A-Za-z0-9_\[\], ]*)\s*\|\s*None\b")

    def repl(match: re.Match[str]) -> str:
        left = match.group(1).strip()
        return f"Optional[{left}]"

    updated, count = pattern.subn(repl, content)
    if count:
        updated = _ensure_optional_import(updated)
    return updated, count


def main() -> int:
    parser = argparse.ArgumentParser(description="GrayShop dijagnostika i brzi popravak")
    parser.add_argument("--fix", action="store_true", help="Pokušaj automatski zamijeniti stare `x | None` anotacije u main.py")
    args = parser.parse_args()

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
    has_legacy = bool(re.search(r"\b\w+\s*\|\s*None\b", content))

    if has_legacy:
        print("[GREŠKA] Ova kopija main.py još sadrži staru anotaciju tipa `x | None`.")
        if args.fix:
            fixed, count = _rewrite_legacy_unions(content)
            if count:
                backup_path = main_path.with_suffix(".py.bak")
                backup_path.write_text(content, encoding="utf-8")
                main_path.write_text(fixed, encoding="utf-8")
                print(f"[OK] Napravljen automatski popravak ({count} zamjena). Backup: {backup_path.name}")
            else:
                print("[UPOZORENJE] Nije pronađen uzorak za automatski popravak.")
        else:
            print("         Pokrenite `python doctor.py --fix` za automatski pokušaj popravka ili napravite `git pull`.")
            return 1

    reloaded = main_path.read_text(encoding="utf-8", errors="replace")
    if re.search(r"\b\w+\s*\|\s*None\b", reloaded):
        print("[GREŠKA] I dalje postoje zastarjele anotacije. Napravite `git pull` i osvježite .venv.")
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
