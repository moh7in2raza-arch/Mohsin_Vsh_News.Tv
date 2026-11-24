# Report and grid heading standardization

## Result

Implemented the approved heading sets as shared constants in
`src/app/ui/report_headings.py` and applied them to active voucher, trial-balance,
general-ledger, accounts, users and employee grids. Voucher detail and entry
grids use the same five headings; the voucher register itself is now a
selection list rather than a differently headed summary grid.

The shared report actions now provide Print Preview, PDF, TXT and Markdown.
Preview and PDF use the same HTML table renderer and supplied headings. TXT is
tab-separated; Markdown is a Markdown table. The Accounts export menu retains
CSV and Excel, with the approved Accounts headings in both formats.

## Approved heading sets

| Screen/report | Headings |
|---|---|
| Voucher | `AcCode`, `Account Head Title`, `Particulars`, `Debit`, `Credit` |
| Trial Balance | `AcCode`, `Account Head Title`, `Opening Bal`, `Total Debit`, `Total Credit`, `Closing Bal` |
| General Ledger | `Date`, `Voucher No`, `Src`, `Particulars / Contra`, `Debit`, `Credit`, `Running Bal` |
| Bank Reconciliation | `Date`, `PV/RV No`, `Party / Account`, `Chq No`, `Chq Date`, `Amount` |
| Users Screen | `UserName`, `Designation`, `Add/Edit Rights`, `Delete Rights`, `Reports Access`, `Backup Restore` |
| Employees Screen | `Employee ID`, `Employee Name`, `Department`, `Designation`, `CNIC`, `Phone No.`, `Joining Date`, `Salary`, `Status` |
| Accounts Screen | `AcCode`, `AcName`, `TypeCode`, `Opening Balance`, `Current Balance`, `Active` |

Balance Sheet section headings are `ASSETS` / `Amount (PKR)` and
`LIABILITIES & CAPITAL` / `Amount (PKR)`, with the approved subgroups
`NON-CURRENT / FIXED ASSETS`, `CURRENT ASSETS (CASH & BANK)`,
`CAPITAL & RESERVES`, and `NON-CURRENT / CURRENT LIABILITIES`.

## Data availability

Balance Sheet and Bank Reconciliation views/data services are not implemented
in the active app, so no screens or fabricated report data were added. Trial
Balance opening balances and General Ledger source values are not provided by
their current report data model; those cells are left blank. Trial Balance
total-debit and total-credit columns use the posted movement totals through the
selected as-of date; closing values use the existing net debit/credit balances.
Accounts has no stored opening/current balance fields, and user records do not
provide designation or per-user rights, so those cells remain blank when absent.
Voucher particulars use the available voucher narration; line-specific
particulars are not stored. Employee listing now reads the existing department
relation and CNIC field.

## Validation

Added tests for the exact approved headings, TXT/Markdown heading output, and
the active UI table headers. The report standardization and Qt shell smoke tests
pass together; `git diff --check` reports no whitespace errors.
