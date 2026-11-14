from decimal import Decimal

import pytest

from src.app.domain.accounting.chart import ACCOUNT_TYPES, normal_balance_for
from src.app.domain.accounting.journal import (
    JournalError,
    make_line,
    reverse_lines,
    validate_balanced,
)


def test_line_needs_exactly_one_side():
    with pytest.raises(JournalError):
        make_line(1, "10", "10")
    with pytest.raises(JournalError):
        make_line(1, "0", "0")


def test_line_rejects_negative_and_float():
    with pytest.raises(JournalError):
        make_line(1, "-5", "0")
    with pytest.raises(TypeError):
        make_line(1, 10.5, "0")


def test_balanced_voucher_returns_total():
    lines = [make_line(1, "100.00", "0"), make_line(2, "0", "100.00")]
    assert validate_balanced(lines) == Decimal("100.00")


def test_unbalanced_voucher_is_rejected():
    lines = [make_line(1, "100", "0"), make_line(2, "0", "99.99")]
    with pytest.raises(JournalError):
        validate_balanced(lines)


def test_single_line_voucher_is_rejected():
    with pytest.raises(JournalError):
        validate_balanced([make_line(1, "100", "0")])


def test_reverse_swaps_sides_and_stays_balanced():
    lines = [make_line(1, "75", "0"), make_line(2, "0", "75")]
    reversed_ = reverse_lines(lines)
    assert reversed_[0].credit == Decimal("75.00") and reversed_[0].debit == 0
    assert validate_balanced(reversed_) == Decimal("75.00")


def test_normal_balance_by_type():
    assert normal_balance_for("Asset") == "D"
    assert normal_balance_for("Income") == "C"
    assert set(ACCOUNT_TYPES) == {"Asset", "Liability", "Equity", "Income", "Expense"}
    with pytest.raises(ValueError):
        normal_balance_for("Other")
        