from decimal import Decimal
import pytest
from src.app.domain.accounting.money import to_decimal, to_minor, from_minor


def test_decimal_has_no_float_drift():
    assert Decimal("0.1") + Decimal("0.2") == Decimal("0.3")


def test_rounds_half_up():
    assert to_minor("2.345") == 235
    assert to_minor("2.344") == 234


def test_round_trip():
    assert from_minor(to_minor("1500.50")) == Decimal("1500.50")


def test_negative_amount():
    assert to_minor("-10.25") == -1025


def test_float_is_refused():
    with pytest.raises(TypeError):
        to_decimal(0.1)
