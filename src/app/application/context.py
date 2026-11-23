"""
The bundle of services the UI receives.
UI code imports this module and application services,
never infrastructure.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app.application.services.account_service import AccountService
    from src.app.application.services.auth_service import AuthService
    from src.app.application.services.employee_service import EmployeeService
    from src.app.application.services.report_service import ReportService
    from src.app.application.services.voucher_service import VoucherService


@dataclass(frozen=True)
class Services:
    auth: "AuthService"
    vouchers: "VoucherService"
    accounts: "AccountService"
    reports: "ReportService"
    employees: "EmployeeService"
    company: "CompanyService | None" = None

