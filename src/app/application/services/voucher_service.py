from datetime import date
from types import SimpleNamespace

from src.app.application.dto import VoucherDetail, VoucherLineRow, VoucherRow
from src.app.application.services.permission_service import PermissionService
from src.app.application.services.posting_service import PostingError, PostingService
from src.app.application.session import Session
from src.app.domain.accounting.journal import (
    JournalError,
    JournalLine,
    make_line,
    reverse_lines,
    totals,
    validate_balanced,
)
from src.app.domain.accounting.voucher_types import VOUCHER_TYPES
from src.app.domain.security import permissions as P
from src.app.domain.workflow import can_transition
from src.app.infrastructure.database.unit_of_work import UnitOfWork


class VoucherError(Exception):
    pass


class VoucherService:
    """Enforces permissions and coordinates voucher workflows. Every operation
    runs in ONE transaction together with its audit record (ADR-0001 s.4)."""

    def __init__(self, uow_factory=UnitOfWork):
        self._uow_factory = uow_factory

    # ---- pure rule (kept: used by tests and by the UI via can_transition) ----
    def transition(self, current_status: str, new_status: str):
        if not can_transition(current_status, new_status):
            raise VoucherError(f"Cannot move from {current_status} to {new_status}")
        return new_status

    # ---- queries ----
    def list_vouchers(
        self, session: Session, status: str | None = None,
        query: str | None = None,
    ) -> list[VoucherRow]:
        PermissionService.require(session.permissions, P.VOUCHER_VIEW)
        with self._uow_factory() as uow:
            normalized_query = (query or "").strip() or None
            return [
                VoucherRow(**r)
                for r in uow.vouchers.list_headers(status, normalized_query)
            ]

    def get_voucher(self, session: Session, voucher_id: int) -> VoucherDetail:
        PermissionService.require(session.permissions, P.VOUCHER_VIEW)
        with self._uow_factory() as uow:
            header = uow.vouchers.get_header(voucher_id)
            if header is None:
                raise VoucherError("Voucher not found")
            lines = [VoucherLineRow(**r) for r in uow.vouchers.get_lines(voucher_id)]
        return VoucherDetail(VoucherRow(**header), lines)

    # ---- commands ----
    def create_draft(self, session: Session, voucher_date: date,
                     narration: str, lines: list[dict], party_name: str = "",
                     cheque_no: str = "", cheque_date: date | None = None,
                     voucher_type: str = "Journal", reference_no: str = "") -> int:
        PermissionService.require(session.permissions, P.VOUCHER_CREATE)
        if not isinstance(voucher_date, date):
            raise VoucherError("Voucher date is required")
        if cheque_date is not None and not isinstance(cheque_date, date):
            raise VoucherError("Cheque date must be a valid date")
        if voucher_type not in VOUCHER_TYPES:
            raise VoucherError("Choose a valid voucher type")
        try:
            journal_lines, persisted_lines = self._prepare_lines(lines)
            validate_balanced(journal_lines)
        except JournalError as ex:
            raise VoucherError(str(ex)) from None
        except (TypeError, KeyError, ArithmeticError):
            raise VoucherError("Invalid account or amount on a voucher line") from None

        with self._uow_factory() as uow:
            if not uow.vouchers.is_period_open(voucher_date, lock=True):
                raise VoucherError("Voucher date is outside an open financial year")
            usable = uow.accounts.usable_ids({l.account_id for l in journal_lines})
            if any(l.account_id not in usable for l in journal_lines):
                raise VoucherError("A voucher line uses an unknown or inactive account")
            account_details = uow.accounts.posting_details(
                {line.account_id for line in journal_lines}
            )
            self._validate_voucher_type(
                voucher_type, journal_lines, account_details, party_name,
                reference_no,
            )
            number = uow.vouchers.next_voucher_no(voucher_date.year, voucher_type)
            voucher_id = uow.vouchers.insert_header(
                number,
                voucher_date,
                (narration or "").strip() or None,
                session.user_id,
                (party_name or "").strip(),
                (cheque_no or "").strip(),
                cheque_date,
                voucher_type,
                (reference_no or "").strip(),
            )
            uow.vouchers.insert_lines(voucher_id, persisted_lines)
            uow.audit.record(session.user_id, "voucher.create", "voucher", voucher_id)
        return voucher_id

    def update_draft(
        self, session: Session, voucher_id: int, voucher_date: date,
        narration: str, lines: list[dict], party_name: str = "",
        cheque_no: str = "", cheque_date: date | None = None,
        voucher_type: str | None = None, reference_no: str = "",
    ) -> None:
        PermissionService.require(session.permissions, P.VOUCHER_EDIT_DRAFT)
        if not isinstance(voucher_date, date):
            raise VoucherError("Voucher date is required")
        if cheque_date is not None and not isinstance(cheque_date, date):
            raise VoucherError("Cheque date must be a valid date")
        if voucher_type is not None and voucher_type not in VOUCHER_TYPES:
            raise VoucherError("Choose a valid voucher type")
        try:
            journal_lines, persisted_lines = self._prepare_lines(lines)
            validate_balanced(journal_lines)
        except JournalError as ex:
            raise VoucherError(str(ex)) from None
        except (TypeError, KeyError, ArithmeticError):
            raise VoucherError("Invalid account or amount on a voucher line") from None

        with self._uow_factory() as uow:
            header = uow.vouchers.get_header(voucher_id, lock=True)
            if header is None:
                raise VoucherError("Voucher not found")
            if header["status"] != "Draft":
                raise VoucherError("Only draft vouchers can be edited")
            if voucher_type is not None and voucher_type != header["voucher_type"]:
                raise VoucherError("Voucher type cannot be changed after creation")
            if not uow.vouchers.is_period_open(voucher_date, lock=True):
                raise VoucherError("Voucher date is outside an open financial year")
            usable = uow.accounts.usable_ids({line.account_id for line in journal_lines})
            if any(line.account_id not in usable for line in journal_lines):
                raise VoucherError("A voucher line uses an unknown or inactive account")
            account_details = uow.accounts.posting_details(
                {line.account_id for line in journal_lines}
            )
            self._validate_voucher_type(
                header["voucher_type"], journal_lines, account_details,
                party_name, reference_no,
            )
            uow.vouchers.update_draft_header(
                voucher_id,
                voucher_date,
                (narration or "").strip() or None,
                (party_name or "").strip(),
                (cheque_no or "").strip(),
                cheque_date,
                (reference_no or "").strip(),
            )
            uow.vouchers.replace_lines(voucher_id, persisted_lines)
            uow.audit.record(
                session.user_id, "voucher.update_draft", "voucher", voucher_id
            )

    @staticmethod
    def _prepare_lines(lines):
        journal_lines = []
        persisted_lines = []
        for line in lines:
            journal_line = make_line(
                line["account_id"],
                line.get("debit", "0"),
                line.get("credit", "0"),
            )
            journal_lines.append(journal_line)
            persisted_lines.append(
                {
                    "account_id": journal_line.account_id,
                    "debit": journal_line.debit,
                    "credit": journal_line.credit,
                    "description": str(line.get("description") or "").strip() or None,
                }
            )
        return journal_lines, persisted_lines

    @staticmethod
    def _validate_voucher_type(
        voucher_type, lines, account_details, party_name, reference_no
    ) -> None:
        cash_lines = [
            line for line in lines
            if account_details[line.account_id]["header_code"] == "ASSET_CASH"
        ]
        if voucher_type == "Payment" and not any(
            line.credit > 0 for line in cash_lines
        ):
            raise VoucherError("A payment voucher must credit a cash or bank account")
        if voucher_type == "Receipt" and not any(
            line.debit > 0 for line in cash_lines
        ):
            raise VoucherError("A receipt voucher must debit a cash or bank account")
        if voucher_type == "Contra":
            cash_debits = {
                line.account_id for line in cash_lines if line.debit > 0
            }
            cash_credits = {
                line.account_id for line in cash_lines if line.credit > 0
            }
            if not any(
                debit_id != credit_id
                for debit_id in cash_debits
                for credit_id in cash_credits
            ):
                raise VoucherError(
                    "A contra voucher must debit one cash/bank account "
                    "and credit another"
                )
        if voucher_type == "Sales":
            if not (party_name or "").strip() or not (reference_no or "").strip():
                raise VoucherError(
                    "Sales vouchers require a customer and invoice reference"
                )
            has_receivable = any(
                line.debit > 0
                and account_details[line.account_id]["type"] == "Asset"
                for line in lines
            )
            has_revenue = any(
                line.credit > 0
                and account_details[line.account_id]["type"] == "Income"
                for line in lines
            )
            if not has_receivable or not has_revenue:
                raise VoucherError(
                    "Sales vouchers must debit an asset and credit revenue"
                )
        if voucher_type == "Purchase":
            if not (party_name or "").strip() or not (reference_no or "").strip():
                raise VoucherError(
                    "Purchase vouchers require a supplier and invoice reference"
                )
            has_purchase = any(
                line.debit > 0
                and account_details[line.account_id]["type"] in {"Asset", "Expense"}
                for line in lines
            )
            has_settlement = any(
                line.credit > 0
                and account_details[line.account_id]["type"]
                in {"Asset", "Liability"}
                for line in lines
            )
            if not has_purchase or not has_settlement:
                raise VoucherError(
                    "Purchase vouchers must debit an asset/expense and "
                    "credit cash, bank, or a payable"
                )

    def submit(self, session: Session, voucher_id: int) -> None:
        self._move(session, voucher_id, "Submitted", P.VOUCHER_SUBMIT, "voucher.submit")

    def approve(self, session: Session, voucher_id: int) -> None:
        self._move(session, voucher_id, "Approved", P.VOUCHER_APPROVE, "voucher.approve")

    def return_to_draft(self, session: Session, voucher_id: int) -> None:
        self._move(session, voucher_id, "Draft", P.VOUCHER_APPROVE, "voucher.return_to_draft")

    def post(self, session: Session, voucher_id: int) -> None:
        PermissionService.require(session.permissions, P.VOUCHER_POST)
        with self._uow_factory() as uow:
            header = self._locked(uow, voucher_id)
            lines = [JournalLine(r["account_id"], r["debit"], r["credit"])
                     for r in uow.vouchers.get_lines(voucher_id)]
            try:
                validate_balanced(lines)
            except JournalError as ex:
                raise VoucherError(str(ex)) from None
            debits, credits = totals(lines)
            period_open = uow.vouchers.is_period_open(
                header["voucher_date"], lock=True
            ) if header["status"] == "Approved" else True
            # PostingService holds the posting rules (status, balance, period)
            try:
                PostingService.post_voucher(
                    SimpleNamespace(status=header["status"], period_closed=not period_open,
                                    debits=debits, credits=credits),
                    session.permissions,
                )
            except PostingError as ex:
                raise VoucherError(str(ex)) from ex
            self.transition(header["status"], "Posted")
            entry_id = uow.vouchers.create_journal_entry(voucher_id, session.user_id)
            uow.vouchers.insert_journal_lines(entry_id, lines)
            uow.vouchers.set_status(voucher_id, "Posted")
            uow.audit.record(session.user_id, "voucher.post", "voucher", voucher_id)

    def reverse(self, session: Session, voucher_id: int) -> None:
        PermissionService.require(session.permissions, P.VOUCHER_REVERSE)
        with self._uow_factory() as uow:
            header = self._locked(uow, voucher_id)
            self.transition(header["status"], "Reversed")
            original = uow.vouchers.find_posting_entry(voucher_id)
            if original is None:
                raise VoucherError("Posted entry not found for this voucher")
            lines = [JournalLine(r["account_id"], r["debit"], r["credit"])
                     for r in uow.vouchers.get_journal_lines(original)]
            entry_id = uow.vouchers.create_journal_entry(
                voucher_id, session.user_id, kind="Reversal", reverses_entry_id=original
            )
            uow.vouchers.insert_journal_lines(entry_id, reverse_lines(lines))
            uow.vouchers.set_status(voucher_id, "Reversed")
            uow.audit.record(session.user_id, "voucher.reverse", "voucher", voucher_id)

    def delete_draft(self, session: Session, voucher_id: int) -> None:
        PermissionService.require(session.permissions, P.VOUCHER_DELETE_DRAFT)
        with self._uow_factory() as uow:
            header = self._locked(uow, voucher_id)
            if header["status"] != "Draft":
                raise VoucherError("Only draft vouchers can be deleted")
            uow.vouchers.delete_draft(voucher_id)
            uow.audit.record(
                session.user_id, "voucher.delete_draft", "voucher", voucher_id
            )

    # ---- helpers ----
    def _locked(self, uow, voucher_id) -> dict:
        header = uow.vouchers.get_header(voucher_id, lock=True)
        if header is None:
            raise VoucherError("Voucher not found")
        return header

    def _move(self, session, voucher_id, new_status, permission, action) -> None:
        PermissionService.require(session.permissions, permission)
        with self._uow_factory() as uow:
            header = self._locked(uow, voucher_id)
            self.transition(header["status"], new_status)
            uow.vouchers.set_status(voucher_id, new_status)
            uow.audit.record(session.user_id, action, "voucher", voucher_id)
