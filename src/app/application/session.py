from dataclasses import dataclass


@dataclass(frozen=True)
class Session:
    user_id: int
    username: str
    permissions: frozenset
    must_change_password: bool = False

    def has(self, code: str) -> bool:
        return code in self.permissions
