"""Seeds a starter chart of accounts (idempotent). Edit STARTER to suit."""
from src.app.domain.accounting.chart import normal_balance_for
from src.app.infrastructure.database.unit_of_work import UnitOfWork

STARTER = [
    ("1000", "Cash in hand", "Asset"),
    ("1010", "Bank", "Asset"),
    ("1100", "Accounts receivable", "Asset"),
    ("1500", "Fixed assets", "Asset"),
    ("2000", "Accounts payable", "Liability"),
    ("2100", "Salaries payable", "Liability"),
    ("3000", "Owner's capital", "Equity"),
    ("3100", "Retained earnings", "Equity"),
    ("4000", "Service income", "Income"),
    ("4100", "Other income", "Income"),
    ("5000", "Salaries expense", "Expense"),
    ("5100", "Rent expense", "Expense"),
    ("5200", "Utilities expense", "Expense"),
    ("5300", "Office expense", "Expense"),
]

if __name__ == "__main__":
    added = 0
    with UnitOfWork() as uow:
        for code, name, kind in STARTER:
            if not uow.accounts.code_exists(code):
                uow.accounts.insert(code, name, kind, normal_balance_for(kind))
                added += 1
        uow.audit.record(None, "accounts.seed", "account", None)
    print(f"Added {added} account(s); {len(STARTER) - added} already existed.")
