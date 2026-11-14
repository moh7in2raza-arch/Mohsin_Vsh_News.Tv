"""Composition root: the only place that wires infrastructure into services."""
from src.app.application.context import Services
from src.app.application.services.account_service import AccountService
from src.app.application.services.auth_service import AuthService
from src.app.application.services.report_service import ReportService
from src.app.application.services.voucher_service import VoucherService
from src.app.infrastructure.logging.setup import configure_logging


def start_logging():
    return configure_logging()


def build_services() -> Services:
    return Services(
        auth=AuthService(),
        vouchers=VoucherService(),
        accounts=AccountService(),
        reports=ReportService(),
    )
