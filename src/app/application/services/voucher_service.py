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
    def list_vouchers(self, session: Session, status: str | None = None) -> list[VoucherRow]:
        PermissionService.require(session.permissions, P.VOUCHER_VIEW)
        with self._uow_factory() as uow:
            return [VoucherRow(**r) for r in uow.vouchers.list_headers(status)]

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
                     narration: str, lines: list[dict]) -> int:
        PermissionService.require(session.permissions, P.VOUCHER_CREATE)
        if not isinstance(voucher_date, date):
            raise VoucherError("Voucher date is required")
        try:
            journal_lines = [
                make_line(l["account_id"], l.get("debit", "0"), l.get("credit", "0"))
                for l in lines
            ]
            validate_balanced(journal_lines)
        except JournalError as ex:
            raise VoucherError(str(ex)) from None
        except (TypeError, KeyError, ArithmeticError):
            raise VoucherError("Invalid account or amount on a voucher line") from None

        with self._uow_factory() as uow:
            usable = uow.accounts.usable_ids({l.account_id for l in journal_lines})
            if any(l.account_id not in usable for l in journal_lines):
                raise VoucherError("A voucher line uses an unknown or inactive account")
            number = uow.vouchers.next_voucher_no(voucher_date.year)
            voucher_id = uow.vouchers.insert_header(
                number, voucher_date, (narration or "").strip() or None, session.user_id
            )
            uow.vouchers.insert_lines(voucher_id, journal_lines)
            uow.audit.record(session.user_id, "voucher.create", "voucher", voucher_id)
        return voucher_id

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
            # PostingService holds the posting rules (status, balance, period)
            try:
                PostingService.post_voucher(
                    SimpleNamespace(status=header["status"], period_closed=False,
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
