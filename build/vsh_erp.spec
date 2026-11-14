# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

ROOT = Path(SPECPATH).parent
MIGRATIONS = ROOT / "src" / "app" / "infrastructure" / "database" / "migrations"

a = Analysis(
    [str(ROOT / "src" / "app" / "main.py")],
    pathex=[str(ROOT)],
    datas=[(str(MIGRATIONS / "*.sql"), "src/app/infrastructure/database/migrations")],
    hiddenimports=["psycopg_binary"],
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="ERPOffice", console=False)
coll = COLLECT(exe, a.binaries, a.datas, name="ERPOffice")
