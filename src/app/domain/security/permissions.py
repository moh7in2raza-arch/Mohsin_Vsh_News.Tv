"""Permission codes used by the application layer (single source of truth)."""

VOUCHER_VIEW = "voucher.view"
VOUCHER_CREATE = "voucher.create"
VOUCHER_EDIT_DRAFT = "voucher.edit_draft"
VOUCHER_SUBMIT = "voucher.submit"
VOUCHER_APPROVE = "voucher.approve"
VOUCHER_POST = "voucher.post"
VOUCHER_REVERSE = "voucher.reverse"
VOUCHER_DELETE_DRAFT = "voucher.delete_draft"
ACCOUNT_VIEW = "account.view"
ACCOUNT_MANAGE = "account.manage"
REPORT_VIEW = "report.view"

ALL = (
    VOUCHER_VIEW, VOUCHER_CREATE, VOUCHER_EDIT_DRAFT, VOUCHER_SUBMIT, VOUCHER_APPROVE,
    VOUCHER_POST, VOUCHER_REVERSE, VOUCHER_DELETE_DRAFT,
    ACCOUNT_VIEW, ACCOUNT_MANAGE, REPORT_VIEW,
)