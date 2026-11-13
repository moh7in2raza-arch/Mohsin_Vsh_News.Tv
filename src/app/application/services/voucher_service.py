from src.app.domain.workflow import can_transition


class VoucherError(Exception):
    pass


class VoucherService:

    def transition(
        self,
        current_status: str,
        new_status: str,
    ):

        if not can_transition(
            current_status,
            new_status,
        ):
            raise VoucherError(
                f"Cannot move from "
                f"{current_status} "
                f"to "
                f"{new_status}"
            )

        return new_status
        