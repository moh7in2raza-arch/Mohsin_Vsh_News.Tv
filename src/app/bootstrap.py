"""
Composition root: the only place that wires infrastructure into services.
"""
from src.app.application.context import Services
from src.app.application.services.account_service import AccountService
from src.app.application.services.auth_service import AuthService
from src.app.application.services.company_service import CompanyService
from src.app.application.services.employee_service import EmployeeService
from src.app.application.services.report_service import ReportService   
from src.app.application.services.voucher_service import VoucherService
from src.app.infrastructure.logging.setup import configure_logging
from src.app.infrastructure.repositories.employee_repository import EmployeeRepository
from src.app.infrastructure.database.connection import get_connection
def start_logging():
    return configure_logging()
def build_services() -> Services:
    conn = get_connection()
    employee_repository = EmployeeRepository(conn)
    return Services(
    auth=AuthService(),
    vouchers=VoucherService(),
    accounts=AccountService(),
    reports=ReportService(),
    employees=EmployeeService(employee_repository),
    company=CompanyService(),
)

