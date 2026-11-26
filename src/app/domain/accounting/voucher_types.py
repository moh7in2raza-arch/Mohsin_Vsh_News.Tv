"""Supported voucher types and their stable numbering prefixes."""

VOUCHER_TYPE_PREFIXES = {
    "Journal": "JV",
    "Payment": "PV",
    "Receipt": "RV",
    "Contra": "CV",
    "Sales": "SV",
    "Purchase": "PU",
}

VOUCHER_TYPES = tuple(VOUCHER_TYPE_PREFIXES)
