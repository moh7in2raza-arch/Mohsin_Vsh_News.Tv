from decimal import Decimal

import pytest

from src.app.application.services.posting_service import PostingError
from src.app.application.services.voucher_service import VoucherError, VoucherService
from src.app.application.session import Session
from src.app.domain.security import permissions as P


class _VoucherRepository:
    def get_header(self, voucher_id, lock=False):
        return {"status": "Draft"}

    def get_lines(self, voucher_id):
        return [
            {"account_id": 1, "debit": Decimal("10"), "credit": Decimal("0")},
            {"account_id": 2, "debit": Decimal("0"), "credit": Decimal("10")},
        ]


class _UnitOfWork:
    def __init__(self):
        self.vouchers = _VoucherRepository()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_post_translates_posting_error_to_voucher_error():
    service = VoucherService(_UnitOfWork)
    session = Session(1, "tester", frozenset({P.VOUCHER_POST}))

    with pytest.raises(VoucherError, match="Only approved vouchers can be posted") as error:
        service.post(session, 1)

    assert isinstance(error.value.__cause__, PostingError)
