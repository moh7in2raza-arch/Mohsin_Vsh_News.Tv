"""Permission codes used by the application layer (single source of truth)."""

VOUCHER_VIEW = "voucher.view"
VOUCHER_CREATE = "voucher.create"
VOUCHER_SUBMIT = "voucher.submit"
VOUCHER_APPROVE = "voucher.approve"
VOUCHER_POST = "voucher.post"
VOUCHER_REVERSE = "voucher.reverse"
ACCOUNT_VIEW = "account.view"
ACCOUNT_MANAGE = "account.manage"
REPORT_VIEW = "report.view"

ALL = (
    VOUCHER_VIEW, VOUCHER_CREATE, VOUCHER_SUBMIT, VOUCHER_APPROVE,
    VOUCHER_POST, VOUCHER_REVERSE, ACCOUNT_VIEW, ACCOUNT_MANAGE, REPORT_VIEW,
)