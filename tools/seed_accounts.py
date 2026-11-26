"""Idempotently seeds the standard chart after the accounting migrations."""
from src.app.domain.accounting.chart import normal_balance_for
from src.app.infrastructure.database.unit_of_work import UnitOfWork

STARTER = [
    ("1000", "Cash in Hand", "Asset", "ASSET_CASH"),
    ("1015", "Cash at Bank", "Asset", "ASSET_CASH"),
    ("1100", "Accounts Receivable", "Asset", "ASSET_RECEIVABLES"),
    ("1200", "Inventory", "Asset", "ASSET_INVENTORY"),
    ("1500", "Fixed Assets", "Asset", "ASSET_FIXED"),
    ("2000", "Accounts Payable", "Liability", "LIABILITY_PAYABLES"),
    ("2010", "Accrued Expenses", "Liability", "LIABILITY_ACCRUED"),
    ("2200", "Loans Payable", "Liability", "LIABILITY_LOANS"),
    ("3200", "Owner Capital", "Equity", "EQUITY_OWNER"),
    ("3100", "Retained Earnings", "Equity", "EQUITY_RETAINED"),
    ("4200", "Sales Revenue", "Income", "INCOME_SALES"),
    ("4300", "Service Revenue", "Income", "INCOME_SERVICE"),
    ("4100", "Other Income", "Income", "INCOME_OTHER"),
    ("5010", "Salary Expense", "Expense", "EXPENSE_SALARY"),
    ("5100", "Rent Expense", "Expense", "EXPENSE_RENT"),
    ("5200", "Utilities Expense", "Expense", "EXPENSE_UTILITIES"),
    ("5300", "Office Expense", "Expense", "EXPENSE_OFFICE"),
    ("5400", "Transport Expense", "Expense", "EXPENSE_TRANSPORT"),
    ("5500", "Miscellaneous Expense", "Expense", "EXPENSE_MISC"),
]

if __name__ == "__main__":
    added = 0
    with UnitOfWork() as uow:
        for code, name, kind, header_code in STARTER:
            if (
                not uow.accounts.code_exists(code)
                and not uow.accounts.name_exists(name, kind)
            ):
                header_id = uow.accounts.header_id_by_code(header_code)
                if header_id is None:
                    raise RuntimeError(
                        "Run tools\\migrate.py to create account headers first"
                    )
                uow.accounts.insert(
                    code, name, kind, normal_balance_for(kind), header_id
                )
                added += 1
        uow.audit.record(None, "accounts.seed", "account", None)
    print(f"Added {added} account(s); {len(STARTER) - added} already existed.")
