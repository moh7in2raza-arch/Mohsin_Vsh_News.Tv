"""One database transaction per business operation (ADR-0001 s.4):
business rows and audit rows commit or roll back together."""
from src.app.infrastructure.database.connection import get_connection
from src.app.infrastructure.repositories.account_repository import AccountRepository
from src.app.infrastructure.repositories.audit_repository import AuditRepository
from src.app.infrastructure.repositories.permission_repository import PermissionRepository
from src.app.infrastructure.repositories.report_repository import ReportRepository
from src.app.infrastructure.repositories.voucher_repository import VoucherRepository


class UnitOfWork:
    def __init__(self, connection=None):
        # An external connection is used by tests: the unit then becomes a
        # savepoint and the caller decides the final commit/rollback.
        self._external = connection
        self._conn = None
        self._tx = None

    def __enter__(self):
        self._conn = self._external if self._external is not None else get_connection()
        self._tx = self._conn.transaction()
        self._tx.__enter__()
        self.vouchers = VoucherRepository(self._conn)
        self.accounts = AccountRepository(self._conn)
        self.audit = AuditRepository(self._conn)
        self.permissions = PermissionRepository(self._conn)
        self.reports = ReportRepository(self._conn)
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            return self._tx.__exit__(exc_type, exc, tb)
        finally:
            if self._external is None:
                self._conn.close()
