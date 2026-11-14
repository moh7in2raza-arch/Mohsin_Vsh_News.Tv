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

        if getattr(voucher, "period_closed", False):
            raise PostingError(
                "Accounting period is closed"
            )

        if (
            getattr(voucher, "debits", 0)
            != getattr(voucher, "credits", 0)
        ):
            raise PostingError(
                "Voucher is not balanced"
            )

        if getattr(voucher, "debits", 0) == 0:
            raise PostingError(
                "Voucher is not balanced"
            )

        return "Posted"