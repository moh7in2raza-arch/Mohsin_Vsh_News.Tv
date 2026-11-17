"""Double-entry rules. Independent of UI and database (ADR-0001 s.4)."""
from dataclasses import dataclass
from decimal import Decimal

from src.app.domain.accounting.money import to_decimal

ZERO = Decimal("0.00")


class JournalError(Exception):
    pass


@dataclass(frozen=True)
class JournalLine:
    account_id: int
    debit: Decimal = ZERO
    credit: Decimal = ZERO


def make_line(account_id, debit="0", credit="0") -> JournalLine:
    d = to_decimal(debit)
    c = to_decimal(credit)
    if d < 0 or c < 0:
        raise JournalError("Amounts cannot be negative")
    if (d > 0) == (c > 0):
        raise JournalError("A line must have a debit or a credit, not both or neither")
    return JournalLine(int(account_id), d, c)


def totals(lines) -> tuple[Decimal, Decimal]:
    return (
        sum((l.debit for l in lines), ZERO),
        sum((l.credit for l in lines), ZERO),
    )


def validate_balanced(lines) -> Decimal:
    """Return the total if balanced, otherwise raise JournalError."""
    if len(lines) < 2:
        raise JournalError("A voucher needs at least two lines")
    debit, credit = totals(lines)
    if debit != credit:
        raise JournalError(f"Voucher is not balanced (debit {debit}, credit {credit})")
    if debit == 0:
        raise JournalError("Voucher total cannot be zero")
    return debit


def reverse_lines(lines) -> list[JournalLine]:
    return [JournalLine(l.account_id, l.credit, l.debit) for l in lines]