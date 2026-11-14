from src.app.application.dto import AccountRow
from src.app.application.services.permission_service import (
    PermissionDenied,
    PermissionService,
)
from src.app.application.session import Session
from src.app.domain.accounting.chart import ACCOUNT_TYPES, normal_balance_for
from src.app.domain.security import permissions as P
from src.app.infrastructure.database.unit_of_work import UnitOfWork


class AccountError(Exception):
    pass


class AccountService:

    def __init__(self, uow_factory=UnitOfWork):
        self._uow_factory = uow_factory

    def list_accounts(self, session: Session, active_only: bool = True) -> list[AccountRow]:
        # Voucher entry and reporting also need the list, not only chart admins
        if not any(session.has(c) for c in (P.ACCOUNT_VIEW, P.REPORT_VIEW, P.VOUCHER_CREATE)):
            raise PermissionDenied(f"Missing permission: {P.ACCOUNT_VIEW}")
        with self._uow_factory() as uow:
            return [AccountRow(**r) for r in uow.accounts.list_all(active_only)]

    def create_account(self, session: Session, code: str, name: str, account_type: str) -> int:
        PermissionService.require(session.permissions, P.ACCOUNT_MANAGE)
        code, name = (code or "").strip(), (name or "").strip()
        if not code or not name:
            raise AccountError("Account code and name are required")
        if account_type not in ACCOUNT_TYPES:
            raise AccountError("Choose a valid account type")
        with self._uow_factory() as uow:
            if uow.accounts.code_exists(code):
                raise AccountError(f"Account code {code} already exists")
            account_id = uow.accounts.insert(code, name, account_type,
                                             normal_balance_for(account_type))
            uow.audit.record(session.user_id, "account.create", "account", account_id)
        return account_id
    