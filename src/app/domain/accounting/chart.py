"""Chart-of-accounts rules (pure domain, no UI or database)."""

# type -> normal balance side (D = debit, C = credit)
ACCOUNT_TYPES = {
    "Asset": "D",
    "Liability": "C",
    "Equity": "C",
    "Income": "C",
    "Expense": "D",
}


def normal_balance_for(account_type: str) -> str:
    try:
        return ACCOUNT_TYPES[account_type]
    except KeyError:
        raise ValueError(f"Unknown account type: {account_type}") from None