from src.app.application.services.permission_service import (
    PermissionService,
)


class PostingError(Exception):
    pass


class PostingService:

    @staticmethod
    def post_voucher(
        voucher,
        user_permissions: set,
    ) -> str:

        PermissionService.require(
            user_permissions,
            "voucher.post",
        )

        if voucher.status != "Approved":
            raise PostingError(
                "Only approved vouchers can be posted"
            )

        return "Posted"