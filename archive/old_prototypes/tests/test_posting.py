import pytest

from src.app.application.services.posting_service import (
    PostingService,
    PostingError,
)


class Voucher:

    def __init__(
        self,
        status,
        period_closed=False,
        debits=100,
        credits=100,
    ):
        self.status = status
        self.period_closed = period_closed
        self.debits = debits
        self.credits = credits


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


def test_closed_period_cannot_post():

    voucher = Voucher(
        "Approved",
        period_closed=True,
    )

    with pytest.raises(PostingError):
        PostingService.post_voucher(
            voucher,
            {"voucher.post"},
        )


def test_unbalanced_voucher_cannot_post():

    voucher = Voucher(
        "Approved",
        debits=100,
        credits=50,
    )

    with pytest.raises(PostingError):
        PostingService.post_voucher(
            voucher,
            {"voucher.post"},
        )