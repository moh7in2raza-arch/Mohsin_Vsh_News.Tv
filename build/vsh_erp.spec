# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

ROOT = Path(SPECPATH).parent
MIGRATIONS = ROOT / "src" / "app" / "infrastructure" / "database" / "migrations"
VOUCHER_TEMPLATE = (
    ROOT / "docs" / "templates" / "vouchers"
    / "Voucher New (2026_09_25 07_06_34 UTC).pdf"
)
VSH_LOGO = ROOT / "assets" / "vsh_logo.png.png"

a = Analysis(
    [str(ROOT / "src" / "app" / "main.py")],
    pathex=[str(ROOT)],
    datas=[
        (str(MIGRATIONS / "*.sql"), "src/app/infrastructure/database/migrations"),
        (str(VOUCHER_TEMPLATE), "docs/templates/vouchers"),
        (str(VSH_LOGO), "assets"),
    ],
    hiddenimports=["psycopg_binary"],
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="ERPOffice", console=False)
coll = COLLECT(exe, a.binaries, a.datas, name="ERPOffice")
