from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from src.app.infrastructure.repositories.user_repository import UserRepository


class AuthError(Exception):
    pass


class AuthService:

    def __init__(self):
        self._user = None
        self._repo = UserRepository()
        self._hasher = PasswordHasher()

    def login(self, username: str, password: str):

        user = self._repo.get_by_username(username)

        if user is None:
            raise AuthError("Invalid username or password")

        if not user["is_active"]:
            raise AuthError("User account is disabled")

        try:
            self._hasher.verify(
                user["password_hash"],
                password
            )
        except VerifyMismatchError:
            raise AuthError("Invalid username or password")

        self._user = user

        return user

    def logout(self):
        self._user = None

    @property
    def current_user(self):
        return self._user
        