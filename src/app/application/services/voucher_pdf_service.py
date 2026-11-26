from __future__ import annotations

import math
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pymupdf

from src.app.application.dto import CompanyProfile, VoucherDetail

_TEMPLATE_RELATIVE_PATH = Path(
    "docs/templates/vouchers/Voucher New (2026_09_25 07_06_34 UTC).pdf"
)
_ROW_RECTS = (
    pymupdf.Rect(39, 270, 327, 296),
    pymupdf.Rect(39, 299, 327, 326),
)
_ACCOUNT_RECTS = (
    pymupdf.Rect(332, 270, 397, 296),
    pymupdf.Rect(332, 299, 397, 326),
)
_DEBIT_RECTS = (
    pymupdf.Rect(401, 270, 482, 296),
    pymupdf.Rect(401, 299, 482, 326),
)
_CREDIT_RECTS = (
    pymupdf.Rect(486, 270, 574, 296),
    pymupdf.Rect(486, 299, 574, 326),
)
_ONES = (
    "Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight",
    "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen",
    "Sixteen", "Seventeen", "Eighteen", "Nineteen",
)
_TENS = (
    "", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy",
    "Eighty", "Ninety",
)
_INDIAN_SCALES = ("Thousand", "Lakh", "Crore", "Arab", "Kharab")


class VoucherPdfError(Exception):
    pass


def _under_thousand(value: int) -> str:
    words = []
    hundreds, remainder = divmod(value, 100)
    if hundreds:
        words.extend((_ONES[hundreds], "Hundred"))
    if remainder >= 20:
        tens, ones = divmod(remainder, 10)
        words.append(_TENS[tens])
        if ones:
            words.append(_ONES[ones])
    elif remainder:
        words.append(_ONES[remainder])
    return " ".join(words)


def _number_in_words(value: int) -> str:
    if value == 0:
        return "Zero"
    groups = []
    remainder = value
    group = remainder % 1000
    if group:
        groups.append(_under_thousand(group))
    remainder //= 1000
    for scale in _INDIAN_SCALES:
        group = remainder % 100
        if group:
            groups.append(f"{_under_thousand(group)} {scale}")
        remainder //= 100
    if remainder:
        raise VoucherPdfError("Voucher total is too large to render in words")
    return " ".join(reversed(groups))


def amount_in_words(amount: Decimal) -> str:
    quantized = Decimal(amount).quantize(Decimal("0.01"))
    if not quantized.is_finite() or quantized < 0:
        raise VoucherPdfError("Voucher total must be a finite, non-negative amount")
    rupees = int(quantized)
    paisa = int((quantized - rupees) * 100)
    result = f"Rupees {_number_in_words(rupees)}"
    if paisa:
        result += f" and Paisa {_number_in_words(paisa)}"
    return result + " Only"


def _resource_root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[4]


class VoucherPdfService:
    def __init__(self, template_path: Path | None = None):
        self._template_path = template_path or (_resource_root() / _TEMPLATE_RELATIVE_PATH)

    def generate(
        self,
        voucher: VoucherDetail,
        company: CompanyProfile,
        output_path: Path,
        printed_at: datetime | None = None,
    ) -> Path:
        output_path = Path(output_path)
        if output_path.resolve() == self._template_path.resolve():
            raise VoucherPdfError("The approved voucher template cannot be overwritten")
        if not self._template_path.is_file():
            raise VoucherPdfError(
                f"Approved voucher template not found: {self._template_path}"
            )
        if not voucher.lines:
            raise VoucherPdfError("Cannot generate a voucher PDF without line items")

        debits = sum((Decimal(line.debit) for line in voucher.lines), Decimal("0"))
        credits = sum((Decimal(line.credit) for line in voucher.lines), Decimal("0"))
        if debits != credits:
            raise VoucherPdfError("Voucher debit and credit totals do not balance")
        words = amount_in_words(debits)
        timestamp = (printed_at or datetime.now().astimezone()).astimezone()
        page_count = math.ceil(len(voucher.lines) / len(_ROW_RECTS))

        try:
            template = pymupdf.open(self._template_path)
            if template.page_count != 1:
                raise VoucherPdfError("Approved voucher template must contain one page")
            output = pymupdf.open()
            for _ in range(page_count):
                output.insert_pdf(template, from_page=0, to_page=0)

            logo_path = self._resolve_logo(company.logo_path)
            for page_number, page in enumerate(output, start=1):
                self._clean_template_page(page)
                self._populate_page(
                    page,
                    voucher,
                    company,
                    logo_path,
                    voucher.lines[
                        (page_number - 1) * len(_ROW_RECTS):
                        page_number * len(_ROW_RECTS)
                    ],
                    words,
                    timestamp,
                    page_number,
                    page_count,
                )

            output.set_metadata({
                "title": (
                    f"{voucher.header.voucher_type} Voucher "
                    f"{voucher.header.voucher_no}"
                ),
                "author": "",
                "subject": "",
                "keywords": "",
                "creator": "VSH NEWS TV ERP",
                "producer": "PyMuPDF",
                "creationDate": "",
                "modDate": "",
            })
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output.save(output_path, garbage=4, deflate=True)
            output.close()
            template.close()
            return output_path
        except VoucherPdfError:
            raise
        except Exception as ex:
            raise VoucherPdfError(f"Could not generate voucher PDF: {ex}") from ex

    def _resolve_logo(self, logo_path: str | None) -> Path | None:
        if not logo_path:
            return None
        configured_path = Path(logo_path)
        candidates = (
            (configured_path,)
            if configured_path.is_absolute()
            else (
                _resource_root() / configured_path,
                Path.cwd() / configured_path,
            )
        )
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        raise VoucherPdfError(f"Configured company logo was not found: {logo_path}")

    @staticmethod
    def _clean_template_page(page) -> None:
        for annotation in list(page.annots() or ()):
            page.delete_annot(annotation)

        redactions = []
        company_span = None
        printing_span = None
        page_number_span = None
        voucher_type_span = None
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", ()):
                for span in line["spans"]:
                    text = span["text"].strip()
                    if text.startswith("Visionary Baluchistan Media Corporation"):
                        company_span = span
                    elif text.startswith("Printing Date/Time:"):
                        printing_span = span
                    elif text == "1 of 1":
                        page_number_span = span
                    elif text == "PAYMENT VOUCHER":
                        voucher_type_span = span
        for span in (
            company_span, printing_span, page_number_span, voucher_type_span
        ):
            if span is not None:
                rect = pymupdf.Rect(span["bbox"])
                rect.x0 -= 1
                rect.y0 -= 1
                rect.x1 += 1
                rect.y1 += 1
                page.add_redact_annot(rect, fill=(1, 1, 1), cross_out=False)
                redactions.append(span)
        if redactions:
            page.apply_redactions(images=0, graphics=0)

    @staticmethod
    def _insert_fitted_text(
        page, rect, text: str, fontsize: float, min_fontsize: float = 6.0,
        align: int = 0,
    ) -> None:
        text = str(text or "").strip()
        if not text:
            return
        while fontsize >= min_fontsize:
            remaining = page.insert_textbox(
                rect,
                text,
                fontname="tiro",
                fontsize=fontsize,
                lineheight=1.0,
                align=align,
                color=(0, 0, 0),
            )
            if remaining >= 0:
                return
            fontsize -= 0.5
        raise VoucherPdfError(f"Voucher field does not fit its approved area: {text[:40]}")

    def _populate_page(
        self,
        page,
        voucher: VoucherDetail,
        company: CompanyProfile,
        logo_path: Path | None,
        lines,
        amount_words: str,
        printed_at: datetime,
        page_number: int,
        page_count: int,
    ) -> None:
        header = voucher.header
        self._insert_fitted_text(
            page, pymupdf.Rect(47, 62, 468, 83), company.company_name, 16, 10
        )
        self._insert_fitted_text(
            page,
            pymupdf.Rect(245, 104, 408, 124),
            f"{header.voucher_type.upper()} VOUCHER",
            13,
            8,
            align=pymupdf.TEXT_ALIGN_CENTER,
        )
        if logo_path is not None:
            for image in page.get_images(full=True):
                page.delete_image(image[0])
            page.insert_image(
                pymupdf.Rect(484.35, 54, 569.95, 127),
                filename=str(logo_path),
                keep_proportion=True,
            )

        self._insert_fitted_text(
            page, pymupdf.Rect(488, 171, 572, 188), header.voucher_no, 10, 7
        )
        self._insert_fitted_text(
            page, pymupdf.Rect(488, 191, 572, 207), header.cheque_no, 10, 7
        )
        cheque_date = (
            header.cheque_date.strftime("%d/%m/%Y")
            if header.cheque_date is not None else ""
        )
        self._insert_fitted_text(
            page, pymupdf.Rect(488, 208, 572, 224), cheque_date, 10, 7
        )
        self._insert_fitted_text(
            page, pymupdf.Rect(88, 203, 410, 220), header.party_name, 11, 8
        )
        self._insert_fitted_text(
            page,
            pymupdf.Rect(98, 220, 410, 237),
            (
                f"{header.narration or ''}  (Ref: {header.reference_no})"
                if header.reference_no else header.narration or ""
            ),
            11,
            8,
        )

        for index, line in enumerate(lines):
            self._insert_fitted_text(
                page, _ROW_RECTS[index], line.description, 9, 6.5
            )
            account_text = f"{line.account_code}\n{line.account_name}"
            self._insert_fitted_text(
                page, _ACCOUNT_RECTS[index], account_text, 7, 4.5
            )
            self._insert_fitted_text(
                page, _DEBIT_RECTS[index], f"{Decimal(line.debit):,.2f}", 9, 7,
                align=pymupdf.TEXT_ALIGN_RIGHT,
            )
            self._insert_fitted_text(
                page, _CREDIT_RECTS[index], f"{Decimal(line.credit):,.2f}", 9, 7,
                align=pymupdf.TEXT_ALIGN_RIGHT,
            )

        self._insert_fitted_text(
            page, pymupdf.Rect(143, 339, 569, 373), amount_words, 11, 7
        )
        print_time = printed_at.strftime("%d/%m/%Y %I:%M:%S %p").lstrip("0")
        self._insert_fitted_text(
            page, pymupdf.Rect(48, 600, 400, 612),
            f"Printing Date/Time:  {print_time}", 9, 7,
        )
        self._insert_fitted_text(
            page, pymupdf.Rect(532, 600, 572, 612),
            f"{page_number} of {page_count}", 9, 7,
        )
