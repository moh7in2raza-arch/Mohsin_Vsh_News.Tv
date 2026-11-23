from datetime import date
from decimal import Decimal

from src.app.application.dto import LedgerRow, TrialBalanceRow
from src.app.application.services.permission_service import PermissionService
from src.app.application.session import Session
from src.app.domain.security import permissions as P
from src.app.infrastructure.database.unit_of_work import UnitOfWork


class ReportService:

    def __init__(self, uow_factory=UnitOfWork):
        self._uow_factory = uow_factory

    def trial_balance(self, session: Session, as_of: date) -> list[TrialBalanceRow]:
        PermissionService.require(session.permissions, P.REPORT_VIEW)
        with self._uow_factory() as uow:
            return [TrialBalanceRow(**r) for r in uow.reports.trial_balance(as_of)]

    def account_ledger(self, session: Session, account_id: int,
                       date_from: date, date_to: date) -> list[LedgerRow]:
        PermissionService.require(session.permissions, P.REPORT_VIEW)
        with self._uow_factory() as uow:
            opening = uow.reports.ledger_opening(account_id, date_from)
            rows = uow.reports.ledger_rows(account_id, date_from, date_to)
        balance = Decimal(opening)
        result = [
            LedgerRow(
                entry_date=None,
                voucher_no="",
                narration="Opening balance",
                debit=Decimal("0.00"),
                credit=Decimal("0.00"),
                balance=balance,
                cheque_no="",
                cheque_date=None,
                party_name="",
            )
        ]
        for r in rows:
            balance += r["debit"] - r["credit"]
            prefix = "Reversal of: " if r["kind"] == "Reversal" else ""
            result.append(
                LedgerRow(
                    entry_date=r["entry_date"],
                    voucher_no=r["voucher_no"],
                    narration=prefix + (r["narration"] or ""),
                    debit=r["debit"],
                    credit=r["credit"],
                    balance=balance,
                    cheque_no=r.get("cheque_no") or "",
                    cheque_date=r.get("cheque_date"),
                    party_name=r.get("party_name") or "",
                )
            )
        return result
