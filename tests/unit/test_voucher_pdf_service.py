from datetime import date, datetime
from decimal import Decimal

import pymupdf

from src.app.application.dto import (
    CompanyProfile,
    VoucherDetail,
    VoucherLineRow,
    VoucherRow,
)
from src.app.application.services.voucher_pdf_service import (
    VoucherPdfService,
    amount_in_words,
)


def _voucher(lines):
    debit = sum((line.debit for line in lines), Decimal("0.00"))
    credit = sum((line.credit for line in lines), Decimal("0.00"))
    return VoucherDetail(
        header=VoucherRow(
            id=1,
            voucher_no="V-2026-000123",
            voucher_date=date(2026, 11, 25),
            narration="November payroll",
            status="Draft",
            debit=debit,
            credit=credit,
            party_name="Payroll",
            cheque_no="CHQ-12",
            cheque_date=date(2026, 11, 25),
            reference_no="SUP-INV-01",
        ),
        lines=lines,
    )


def _line(account_id, code, name, debit, credit, description):
    return VoucherLineRow(
        account_id=account_id,
        account_code=code,
        account_name=name,
        debit=Decimal(debit),
        credit=Decimal(credit),
        description=description,
    )


def test_amount_in_words_uses_rupees_and_paisa():
    assert amount_in_words(Decimal("123.45")) == (
        "Rupees One Hundred Twenty Three and Paisa Forty Five Only"
    )
    assert amount_in_words(Decimal("100000.00")) == "Rupees One Lakh Only"


def test_generate_removes_annotations_and_replaces_sample_values(tmp_path):
    voucher = _voucher([
        _line(1, "5400000005", "Salaries", "123.45", "0", "November salary"),
        _line(2, "1101010001", "Petty Cash", "0", "123.45", "Cash payment"),
    ])
    output_path = tmp_path / "voucher.pdf"
    printed_at = datetime(2026, 11, 25, 12, 30)

    VoucherPdfService().generate(
        voucher,
        CompanyProfile(
            company_name="Test Company",
            address="",
            phone="",
            logo_path=None,
        ),
        output_path,
        printed_at=printed_at,
    )

    with pymupdf.open(output_path) as document:
        assert document.page_count == 1
        page = document[0]
        text = page.get_text()
        assert list(page.annots() or ()) == []
        assert "Test Company" in text
        assert "V-2026-000123" in text
        assert "JOURNAL VOUCHER" in text
        assert "Payroll" in text
        assert "CHQ-12" in text
        assert "Ref: SUP-INV-01" in text
        assert "November salary" in text
        assert "Salaries" in text
        assert "Rupees One Hundred Twenty Three and Paisa Forty Five Only" in text
        assert "25/11/2026" in text
        assert "17/09/2026" not in text
        assert "MohsinDev" not in text
        assert "tester" not in text
        assert "Prepared By" in text and "Verified By" in text


def test_generate_paginates_more_than_two_lines(tmp_path):
    voucher = _voucher([
        _line(1, "A-1", "First account", "60", "0", "Line one"),
        _line(2, "A-2", "Second account", "40", "0", "Line two"),
        _line(3, "A-3", "Third account", "0", "100", "Line three"),
    ])
    output_path = tmp_path / "voucher.pdf"

    VoucherPdfService().generate(
        voucher,
        CompanyProfile("Test Company", "", "", logo_path=None),
        output_path,
        printed_at=datetime(2026, 11, 25, 12, 30),
    )

    with pymupdf.open(output_path) as document:
        assert document.page_count == 2
        assert "1 of 2" in document[0].get_text()
        assert "2 of 2" in document[1].get_text()
        assert "Line three" in document[1].get_text()
