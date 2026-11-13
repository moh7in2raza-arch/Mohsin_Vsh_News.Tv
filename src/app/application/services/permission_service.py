class PermissionDenied(Exception):
    pass


class PermissionService:

    @staticmethod
    def require(
        user_permissions: set,
        permission_code: str,
    ):

        if permission_code not in user_permissions:
            raise PermissionDenied(
                f"Missing permission: {permission_code}"
            )
            