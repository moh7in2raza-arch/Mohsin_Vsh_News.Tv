import logging

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError

from src.app.application.session import Session
from src.app.infrastructure.database.unit_of_work import UnitOfWork
from src.app.infrastructure.repositories.user_repository import UserRepository

log = logging.getLogger(__name__)


class AuthError(Exception):
    pass


class AuthService:

    def __init__(self, uow_factory=UnitOfWork, user_repo=None):
        self._uow_factory = uow_factory
        self._repo = user_repo or UserRepository()
        self._hasher = PasswordHasher()
        self._session: Session | None = None

    def login(self, username: str, password: str) -> Session:
        username = (username or "").strip()
        user = self._repo.get_by_username(username) if username else None

        if user is None or not self._password_ok(user, password):
            self._audit_failure(username, user)
            raise AuthError("Invalid username or password")

        if not user["is_active"]:
            raise AuthError("User account is disabled")

        with self._uow_factory() as uow:
            permissions = uow.permissions.codes_for_user(user["id"])
            uow.audit.record(user["id"], "auth.login", "user", user["id"])

        self._session = Session(
            user_id=user["id"],
            username=user["username"],
            permissions=permissions,
            must_change_password=bool(user["must_change_password"]),
        )
        return self._session

    def logout(self) -> None:
        if self._session is not None:
            try:
                with self._uow_factory() as uow:
                    uow.audit.record(self._session.user_id, "auth.logout", "user",
                                     self._session.user_id)
            except Exception:
                log.exception("Could not write logout audit record")
        self._session = None

    @property
    def current_session(self) -> Session | None:
        return self._session

    def _password_ok(self, user, password) -> bool:
        try:
            return self._hasher.verify(user["password_hash"], password)
        except VerificationError:
            return False

    def _audit_failure(self, username, user) -> None:
        try:
            with self._uow_factory() as uow:
                uow.audit.record(user["id"] if user else None, "auth.login_failed",
                                 username[:100] or None, None)
        except Exception:
            log.exception("Could not write failed-login audit record")
            