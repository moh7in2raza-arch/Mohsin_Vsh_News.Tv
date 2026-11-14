class VoucherRepository:

    def get_voucher(self, voucher_id: int):
        raise NotImplementedError

    def create_journal_entry(self, voucher):
        raise NotImplementedError

    def create_journal_line(
        self,
        entry_id: int,
        line,
    ):
        raise NotImplementedError

    def set_voucher_status(
        self,
        voucher_id: int,
        status: str,
    ):
        raise NotImplementedError

    def audit(
        self,
        user_id: int,
        action: str,
        entity: str,
        entity_id: int,
    ):
        raise NotImplementedError