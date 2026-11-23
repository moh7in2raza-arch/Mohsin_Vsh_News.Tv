from src.app.application.dto import CompanyProfile
from src.app.application.services.permission_service import PermissionService
from src.app.application.session import Session
from src.app.domain.security import permissions as P
from src.app.infrastructure.database.unit_of_work import UnitOfWork

DEFAULT_COMPANY = CompanyProfile(
    company_name="Visionary Baluchistan Media Corporation Pvt Ltd",
    address="Vsh News TV Station Office: Uzma Arcade, Suite 201, 2nd Floor, Khayaban-e-Iqbal, Block 7, Clifton, Karachi.",
    phone="92-21-35308112, 92-21-35308113, 92-21-35308114",
    email="info@vshnews.tv",
    website="www.vshnews.tv",
    logo_path="assets/vsh_logo.png.png",
    tax_number="",
)


class CompanyService:
    def __init__(self, uow_factory=UnitOfWork):
        self._uow_factory = uow_factory

    def get_profile(self, session: Session | None = None) -> CompanyProfile:
        try:
            with self._uow_factory() as uow:
                row = uow.company.get_settings()
                if row:
                    return CompanyProfile(**row)
        except Exception:
            pass
        return DEFAULT_COMPANY

    def update_profile(
        self,
        session: Session,
        company_name: str,
        address: str,
        phone: str,
        email: str = "",
        website: str = "",
        tax_number: str = "",
    ) -> CompanyProfile:
        PermissionService.require(session.permissions, getattr(P, "USER_MANAGE", "user.manage"))
        with self._uow_factory() as uow:
            row = uow.company.save_settings(
                company_name=company_name.strip(),
                address=address.strip(),
                phone=phone.strip(),
                email=email.strip(),
                website=website.strip(),
                tax_number=tax_number.strip(),
            )
            uow.audit.record(
                actor_id=session.user_id,
                action="company.profile.update",
                entity_type="company_settings",
                entity_id="TRUE",
                details={"company_name": company_name.strip()},
            )
            return CompanyProfile(**row)
