"""Plain data handed to the UI. The UI never sees repositories or SQL rows."""
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
    total_debit: Decimal = Decimal("0.00")
    total_credit: Decimal = Decimal("0.00")


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
