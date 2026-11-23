from pathlib import Path

ROOT = Path(r"C:\Mohsin_Vsh_News.tv")

# 1. Migration 0010: Seed official Clifton Karachi company profile & add cheque/party columns to voucher_headers
(ROOT / "src/app/infrastructure/database/migrations/0010_company_and_statement_fields.sql").write_text("""
INSERT INTO company_settings (id, company_name, address, phone, email, website, logo_path, tax_number)
VALUES (
    TRUE,
    'Visionary Baluchistan Media Corporation Pvt Ltd',
    'Vsh News TV Station Office: Uzma Arcade, Suite 201, 2nd Floor, Khayaban-e-Iqbal, Block 7, Clifton, Karachi.',
    '92-21-35308112, 92-21-35308113, 92-21-35308114',
    'info@vshnews.tv',
    'www.vshnews.tv',
    'assets/vsh_logo.png.png',
    ''
)
ON CONFLICT (id) DO UPDATE SET
    company_name = EXCLUDED.company_name,
    address = EXCLUDED.address,
    phone = EXCLUDED.phone;

ALTER TABLE voucher_headers
    ADD COLUMN IF NOT EXISTS cheque_no TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS cheque_date DATE NULL,
    ADD COLUMN IF NOT EXISTS party_name TEXT NOT NULL DEFAULT '';
""", encoding="utf-8")

# 2. CompanyRepository (infrastructure/repositories/company_repository.py)
(ROOT / "src/app/infrastructure/repositories/company_repository.py").write_text("""from src.app.infrastructure.repositories._sql import fetch_one


class CompanyRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_settings(self) -> dict | None:
        return fetch_one(
            self.conn,
            \"\"\"SELECT company_name, address, phone, email, website, logo_path, tax_number
               FROM company_settings WHERE id = TRUE\"\"\",
        )

    def save_settings(
        self,
        company_name: str,
        address: str,
        phone: str,
        email: str = "",
        website: str = "",
        logo_path: str | None = None,
        tax_number: str | None = None,
    ) -> dict:
        row = fetch_one(
            self.conn,
            \"\"\"INSERT INTO company_settings
                   (id, company_name, address, phone, email, website, logo_path, tax_number)
               VALUES (TRUE, %s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (id) DO UPDATE SET
                   company_name = EXCLUDED.company_name,
                   address = EXCLUDED.address,
                   phone = EXCLUDED.phone,
                   email = EXCLUDED.email,
                   website = EXCLUDED.website,
                   logo_path = COALESCE(EXCLUDED.logo_path, company_settings.logo_path),
                   tax_number = EXCLUDED.tax_number
               RETURNING company_name, address, phone, email, website, logo_path, tax_number\"\"\",
            (company_name, address, phone, email, website, logo_path, tax_number),
        )
        return row or {}
""", encoding="utf-8")

# 3. Update ReportRepository to return cheque_no, cheque_date, party_name for Statement of Account
(ROOT / "src/app/infrastructure/repositories/report_repository.py").write_text("""from src.app.infrastructure.repositories._sql import fetch_all, fetch_one

_FROM = \"\"\"
    FROM journal_lines jl
    JOIN journal_entries je ON je.id = jl.entry_id
    JOIN voucher_headers vh ON vh.id = je.voucher_id
\"\"\"


class ReportRepository:
    def __init__(self, conn):
        self.conn = conn

    def trial_balance(self, as_of) -> list[dict]:
        return fetch_all(
            self.conn,
            \"\"\"SELECT a.code, a.name,
                      GREATEST(SUM(jl.debit) - SUM(jl.credit), 0)  AS debit,
                      GREATEST(SUM(jl.credit) - SUM(jl.debit), 0)  AS credit\"\"\"
            + _FROM
            + \"\"\" JOIN accounts a ON a.id = jl.account_id
                  WHERE vh.voucher_date <= %s
                  GROUP BY a.code, a.name ORDER BY a.code\"\"\",
            (as_of,),
        )

    def ledger_opening(self, account_id, date_from):
        row = fetch_one(
            self.conn,
            "SELECT COALESCE(SUM(jl.debit) - SUM(jl.credit), 0) AS net" + _FROM
            + " WHERE jl.account_id = %s AND vh.voucher_date < %s",
            (account_id, date_from),
        )
        return row["net"]

    def ledger_rows(self, account_id, date_from, date_to) -> list[dict]:
        return fetch_all(
            self.conn,
            \"\"\"SELECT vh.voucher_date AS entry_date,
                      vh.voucher_no,
                      COALESCE(vh.cheque_no, '') AS cheque_no,
                      vh.cheque_date,
                      COALESCE(vh.party_name, '') AS party_name,
                      je.kind,
                      vh.narration,
                      jl.debit,
                      jl.credit\"\"\" + _FROM
            + \"\"\" WHERE jl.account_id = %s AND vh.voucher_date BETWEEN %s AND %s
                  ORDER BY vh.voucher_date, je.id, jl.id\"\"\",
            (account_id, date_from, date_to),
        )
""", encoding="utf-8")

# 4. Update UnitOfWork to expose uow.company
uow_path = ROOT / "src/app/infrastructure/database/unit_of_work.py"
uow_txt = uow_path.read_text(encoding="utf-8")
if "CompanyRepository" not in uow_txt:
    uow_txt = uow_txt.replace(
        "from src.app.infrastructure.repositories.account_repository import (",
        "from src.app.infrastructure.repositories.company_repository import CompanyRepository\nfrom src.app.infrastructure.repositories.account_repository import (",
    )
    uow_txt = uow_txt.replace(
        "self.reports = ReportRepository(self._conn)",
        "self.reports = ReportRepository(self._conn)\n        self.company = CompanyRepository(self._conn)",
    )
    uow_path.write_text(uow_txt, encoding="utf-8")

# 5. Update dto.py (CompanyProfile DTO + 9-column LedgerRow with defaults for backwards compatibility)
(ROOT / "src/app/application/dto.py").write_text("""\"\"\"Plain data handed to the UI. The UI never sees repositories or SQL rows.\"\"\"
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class CompanyProfile:
    company_name: str
    address: str
    phone: str
    email: str = ""
    website: str = ""
    logo_path: str | None = None
    tax_number: str | None = None


@dataclass(frozen=True)
class VoucherRow:
    id: int
    voucher_no: str
    voucher_date: date
    narration: str | None
    status: str
    debit: Decimal
    credit: Decimal


@dataclass(frozen=True)
class VoucherLineRow:
    account_id: int
    account_code: str
    account_name: str
    debit: Decimal
    credit: Decimal


@dataclass(frozen=True)
class VoucherDetail:
    header: VoucherRow
    lines: list = field(default_factory=list)


@dataclass(frozen=True)
class AccountRow:
    id: int
    code: str
    name: str
    type: str
    normal_balance: str
    is_active: bool


@dataclass(frozen=True)
class TrialBalanceRow:
    code: str
    name: str
    debit: Decimal
    credit: Decimal


@dataclass(frozen=True)
class LedgerRow:
    entry_date: date | None
    voucher_no: str
    narration: str
    debit: Decimal
    credit: Decimal
    balance: Decimal
    cheque_no: str = ""
    cheque_date: date | None = None
    party_name: str = ""
""", encoding="utf-8")

# 6. CompanyService (application/services/company_service.py)
(ROOT / "src/app/application/services/company_service.py").write_text("""from src.app.application.dto import CompanyProfile
from src.app.application.services.permission_service import PermissionService
from src.app.application.session import Session
from src.app.domain.security import permissions as P
from src.app.infrastructure.database.unit_of_work import UnitOfWork

DEFAULT_COMPANY = CompanyProfile(
    company_name="Visionary Baluchistan Media Corporation Pvt Ltd",
    address="Vsh News TV Station Office: Uzma Arcade, Suite 201, 2nd Floor, Khayaban-e-Iqbal, Block 7, Clifton, Karachi.",
    phone="92-21-35308112, 92-21-35308113, 92-21-35308114",
    email="info@vshnews.tv",
    website="www.vshnews.tv",
    logo_path="assets/vsh_logo.png.png",
    tax_number="",
)


class CompanyService:
    def __init__(self, uow_factory=UnitOfWork):
        self._uow_factory = uow_factory

    def get_profile(self, session: Session | None = None) -> CompanyProfile:
        try:
            with self._uow_factory() as uow:
                row = uow.company.get_settings()
                if row:
                    return CompanyProfile(**row)
        except Exception:
            pass
        return DEFAULT_COMPANY

    def update_profile(
        self,
        session: Session,
        company_name: str,
        address: str,
        phone: str,
        email: str = "",
        website: str = "",
        tax_number: str = "",
    ) -> CompanyProfile:
        PermissionService.require(session.permissions, getattr(P, "USER_MANAGE", "user.manage"))
        with self._uow_factory() as uow:
            row = uow.company.save_settings(
                company_name=company_name.strip(),
                address=address.strip(),
                phone=phone.strip(),
                email=email.strip(),
                website=website.strip(),
                tax_number=tax_number.strip(),
            )
            uow.audit.record(
                actor_id=session.user_id,
                action="company.profile.update",
                entity_type="company_settings",
                entity_id="TRUE",
                details={"company_name": company_name.strip()},
            )
            return CompanyProfile(**row)
""", encoding="utf-8")

# 7. Update ReportService so account_ledger populates all 9 Statement of Account fields
(ROOT / "src/app/application/services/report_service.py").write_text("""from datetime import date
from decimal import Decimal

from src.app.application.dto import LedgerRow, TrialBalanceRow
from src.app.application.services.permission_service import PermissionService
from src.app.application.session import Session
from src.app.domain.security import permissions as P
from src.app.infrastructure.database.unit_of_work import UnitOfWork
class ReportService:
def init(self, uow_factory=UnitOfWork):
self._uow_factory = uow_factory
def trial_balance(self, session: Session, as_of: date) -> list[TrialBalanceRow]:
PermissionService.require(session.permissions, P.REPORT_VIEW)
with self._uow_factory() as uow:
return [TrialBalanceRow(**r) for r in uow.reports.trial_balance(as_of)]
def account_ledger(self, session: Session, account_id: int,
date_from: date, date_to: date) -> list[LedgerRow]:
PermissionService.require(session.permissions, P.REPORT_VIEW)
with self._uow_factory() as uow:
opening = uow.reports.ledger_opening(account_id, date_from)
rows = uow.reports.ledger_rows(account_id, date_from, date_to)
balance = Decimal(opening)
result = [
LedgerRow(
entry_date=None,
voucher_no="",
narration="Opening balance",
debit=Decimal("0.00"),
credit=Decimal("0.00"),
balance=balance,
cheque_no="",
cheque_date=None,
party_name="",
)
]
for r in rows:
balance += r["debit"] - r["credit"]
prefix = "Reversal of: " if r["kind"] == "Reversal" else ""
result.append(
LedgerRow(
entry_date=r["entry_date"],
voucher_no=r["voucher_no"],
narration=prefix + (r["narration"] or ""),
debit=r["debit"],
credit=r["credit"],
balance=balance,
cheque_no=r.get("cheque_no") or "",
cheque_date=r.get("cheque_date"),
party_name=r.get("party_name") or "",
)
)
return result
""", encoding="utf-8")
