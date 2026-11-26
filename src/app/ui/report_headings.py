"""Approved headings shared by application tables and report exports."""

VOUCHER_HEADINGS = (
    "AcCode",
    "Account Head Title",
    "Description",
    "Debit",
    "Credit",
)

TRIAL_BALANCE_HEADINGS = (
    "AcCode",
    "Account Head Title",
    "Opening Bal",
    "Total Debit",
    "Total Credit",
    "Closing Bal",
)

GENERAL_LEDGER_HEADINGS = (
    "Date",
    "Voucher No",
    "Src",
    "Particulars / Contra",
    "Debit",
    "Credit",
    "Running Bal",
)

BANK_RECONCILIATION_HEADINGS = (
    "Date",
    "PV/RV No",
    "Party / Account",
    "Chq No",
    "Chq Date",
    "Amount",
)

USERS_HEADINGS = (
    "UserName",
    "Designation",
    "Add/Edit Rights",
    "Delete Rights",
    "Reports Access",
    "Backup Restore",
)

EMPLOYEES_HEADINGS = (
    "Employee ID",
    "Employee Name",
    "Department",
    "Designation",
    "CNIC",
    "Phone No.",
    "Joining Date",
    "Salary",
    "Status",
)

ACCOUNTS_HEADINGS = (
    "AcCode",
    "AcName",
    "Account Group",
    "Account Header",
    "Opening Balance",
    "Current Balance",
    "Active",
)

BALANCE_SHEET_ASSET_HEADINGS = ("ASSETS", "Amount (PKR)")
BALANCE_SHEET_LIABILITY_HEADINGS = ("LIABILITIES & CAPITAL", "Amount (PKR)")
BALANCE_SHEET_SUBGROUPS = (
    "NON-CURRENT / FIXED ASSETS",
    "CURRENT ASSETS (CASH & BANK)",
    "CAPITAL & RESERVES",
    "NON-CURRENT / CURRENT LIABILITIES",
)
