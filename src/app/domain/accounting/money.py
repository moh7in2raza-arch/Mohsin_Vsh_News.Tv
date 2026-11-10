from decimal import Decimal, ROUND_HALF_UP

_TWO_PLACES = Decimal("0.01")


def to_decimal(value) -> Decimal:
    """Convert int, str or Decimal to a 2-place Decimal. Floats are refused."""
    if isinstance(value, float):
        raise TypeError("Floats are not allowed for money; use Decimal or str")
    return Decimal(value).quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)


def to_minor(amount) -> int:
    """Decimal amount -> integer minor units (paisa)."""
    return int(to_decimal(amount) * 100)


def from_minor(minor: int) -> Decimal:
    """Integer minor units -> Decimal with 2 places."""
    return (Decimal(minor) / 100).quantize(_TWO_PLACES)
