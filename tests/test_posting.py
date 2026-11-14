import pytest

from src.app.application.services.posting_service import (
    PostingService,
    PostingError,
)


class Voucher:
    def __init__(self, status):
        self.status = status


def test_only_approved_vouchers_can_be_posted():
    voucher = Voucher("Draft")

    with pytest.raises(PostingError):
        PostingService.post_voucher(
            voucher,
            {"voucher.post"},
        )


def test_posting_changes_status():
    voucher = Voucher("Approved")

    result = PostingService.post_voucher(
        voucher,
        {"voucher.post"},
    )

    assert result == "Posted"