# VSH NEWS TV ERP — Visual Mockup Specification

**Status:** Visual design review package • **Revision:** 1.0 • **Date:** 2026-11-25

This package contains 14 paired screen/A4 print-PDF wireframe images. Each image is a standalone SVG vector preview with the repository VSH NEWS TV logo embedded. The left panel is the ERP screen; the right panel is the complete printable page. All employee, voucher, ledger and dashboard values are fictional demonstration data and are explicitly marked **DEMO / NOT LIVE**.

## Visual conventions

- Brand: repository logo asset; VSH navy `#17365D`, deep navy `#102A43`, white, light gray `#F1F4F7`, and gray rules/text. Company legal name follows the existing application design; contact/tax values are shown as company-profile placeholders rather than invented facts.
- Page format: A4 portrait or landscape as specified in the source design system. The print panel is a fixed page with a shared company header, metadata, footer, page number and signature fields. PDF is intended to match print preview exactly.
- All data and references shown are fictional. Signature lines are intentionally blank. These are conceptual mockups, not operational forms or valid accounting records.
- The Employee Application Form image is schematic only: the existing approved DOCX master remains immutable and is the sole source for the production print/PDF layout. The schematic does not replace its coordinates, wording, page count or signature areas.
- Formal HR letters show a reserved approved-wording area only. Obtain the approved DOCX master and authorized wording before generating an official letter.

## Mockup index

| # | Deliverable | Page | Paired image |
|---:|---|---|---|
| 1 | Dashboard | A4 landscape | [Open SVG](mockups/01_dashboard.svg) |
| 2 | Employee Information Form | A4 portrait | [Open SVG](mockups/02_employee_information.svg) |
| 3 | Employee Application Form | A4 portrait | [Open SVG](mockups/03_employee_application.svg) |
| 4 | Appointment Letter | A4 portrait | [Open SVG](mockups/04_appointment_letter.svg) |
| 5 | Experience Letter | A4 portrait | [Open SVG](mockups/05_experience_letter.svg) |
| 6 | Salary Certificate | A4 portrait | [Open SVG](mockups/06_salary_certificate.svg) |
| 7 | No Objection Certificate | A4 portrait | [Open SVG](mockups/07_noc.svg) |
| 8 | Payment Voucher | A4 portrait | [Open SVG](mockups/08_payment_voucher.svg) |
| 9 | Receipt Voucher | A4 portrait | [Open SVG](mockups/09_receipt_voucher.svg) |
| 10 | Journal Voucher | A4 portrait | [Open SVG](mockups/10_journal_voucher.svg) |
| 11 | General Ledger | A4 landscape | [Open SVG](mockups/11_general_ledger.svg) |
| 12 | Account Ledger | A4 landscape | [Open SVG](mockups/12_account_ledger.svg) |
| 13 | Trial Balance | A4 portrait | [Open SVG](mockups/13_trial_balance.svg) |
| 14 | Employee Master Report | A4 landscape | [Open SVG](mockups/14_employee_master_report.svg) |

## Individual specifications

### 1. Dashboard

**Page:** A4 landscape • **Screen:** Dashboard workspace with contextual actions, status and A4 preview. **Print/PDF:** Landscape KPI snapshot with status summary and recent activity.

**Header/company:** Embedded VSH logo, VSH NEWS TV and Visionary Baluchistan Media Corporation (Pvt) Ltd; contact and tax details resolve from the company profile. **Sample data:** Active staff: 128 (sample); Departments: 08 (sample); Pending approvals: 06 (sample); Payroll period: Nov 2026 (sample); **Workspace snapshot:** Logged-in user = HR Manager (Sample), Role = HR / Read only, Company = VSH NEWS TV.

**Table columns:** Activity, Reference, Date, State.

**Signatures:** Optional prepared/reviewed sign-off for a printed dashboard snapshot; not a live operational approval.

**Image:** [Paired screen and print mockup](mockups/01_dashboard.svg).

### 2. Employee Information Form

**Page:** A4 portrait • **Screen:** HR / Employees workspace with contextual actions, status and A4 preview. **Print/PDF:** Portrait employee profile with identity, contact, employment, and compensation blocks.

**Header/company:** Embedded VSH logo, VSH NEWS TV and Visionary Baluchistan Media Corporation (Pvt) Ltd; contact and tax details resolve from the company profile. **Sample data:** **Identity:** Employee ID = VSH-104, Full name = Nadia Karim (Sample), CNIC = XXXXX-XXXXXXX-X, Status = Active; **Contact:** Phone = 03XX-1234567, Email = nadia.sample@example.test; **Employment:** Department = News, Designation = Reporter, Joining date = 12-May-2024; **Compensation:** Monthly salary = PKR 125,000.00, As of = 25-Nov-2026.

**Table columns:** —.

**Signatures:** Prepared/verified and employee acknowledgement lines; blank for manual signing.

**Image:** [Paired screen and print mockup](mockups/02_employee_information.svg).

### 3. Employee Application Form

**Page:** A4 portrait • **Screen:** HR / Employees workspace with contextual actions, status and A4 preview. **Print/PDF:** Schematic view of mapped fields only; actual approved DOCX master retains its exact page structure, wording, layout and signatures.

**Header/company:** Embedded VSH logo, VSH NEWS TV and Visionary Baluchistan Media Corporation (Pvt) Ltd; contact and tax details resolve from the company profile. **Sample data:** **Personal information:** Full name = Nadia Karim (Sample), CNIC = XXXXX-XXXXXXX-X, Joining date = 12-May-2024, Personal phone = 03XX-1234567; **Position & compensation:** Designation = Reporter, Department = News, Monthly salary = PKR 125,000.00, Employee ID = VSH-104.

**Table columns:** —.

**Signatures:** The approved master’s original signature areas are intentionally not recreated or populated. Use the fixed master for production.

**Image:** [Paired screen and print mockup](mockups/03_employee_application.svg).

### 4. Appointment Letter

**Page:** A4 portrait • **Screen:** HR / Letters workspace with contextual actions, status and A4 preview. **Print/PDF:** Formal portrait letter: recipient block, approved text area, appointment metadata, acceptance and authorized signatory.

**Header/company:** Embedded VSH logo, VSH NEWS TV and Visionary Baluchistan Media Corporation (Pvt) Ltd; contact and tax details resolve from the company profile. **Sample data:** **Recipient:** Employee = Nadia Karim (Sample), Employee ID = VSH-104, Designation = Reporter, Department = News; **Appointment details:** Issue date = 25-Nov-2026, Effective date = 01-Dec-2026, Location = Quetta (Sample).

**Table columns:** —.

**Signatures:** Employee acceptance and authorized signatory; names/dates remain blank.

**Image:** [Paired screen and print mockup](mockups/04_appointment_letter.svg).

### 5. Experience Letter

**Page:** A4 portrait • **Screen:** HR / Letters workspace with contextual actions, status and A4 preview. **Print/PDF:** Portrait certificate/letter with employee identity, verified service period, approved body and signatory.

**Header/company:** Embedded VSH logo, VSH NEWS TV and Visionary Baluchistan Media Corporation (Pvt) Ltd; contact and tax details resolve from the company profile. **Sample data:** **Employee:** Name = Nadia Karim (Sample), Employee ID = VSH-104, Designation = Reporter, Department = News; **Verified period:** From = 12-May-2024, To = Current (sample), Issue date = 25-Nov-2026.

**Table columns:** —.

**Signatures:** Authorized signatory name/title/signature/date; leave signature blank.

**Image:** [Paired screen and print mockup](mockups/05_experience_letter.svg).

### 6. Salary Certificate

**Page:** A4 portrait • **Screen:** HR / Letters workspace with contextual actions, status and A4 preview. **Print/PDF:** Confidential portrait certificate with employee identity, salary amount and as-of date, approved certification body.

**Header/company:** Embedded VSH logo, VSH NEWS TV and Visionary Baluchistan Media Corporation (Pvt) Ltd; contact and tax details resolve from the company profile. **Sample data:** **Employee:** Name = Nadia Karim (Sample), Employee ID = VSH-104, Designation = Reporter, Department = News; **Salary details:** Monthly salary = PKR 125,000.00, Effective / as of = 25-Nov-2026, Issue date = 25-Nov-2026.

**Table columns:** —.

**Signatures:** Authorized signatory name/title/signature/date; blank for signing.

**Image:** [Paired screen and print mockup](mockups/06_salary_certificate.svg).

### 7. No Objection Certificate

**Page:** A4 portrait • **Screen:** HR / Letters workspace with contextual actions, status and A4 preview. **Print/PDF:** Portrait certificate with recipient, employee identity, approved purpose/validity and authorized signatory.

**Header/company:** Embedded VSH logo, VSH NEWS TV and Visionary Baluchistan Media Corporation (Pvt) Ltd; contact and tax details resolve from the company profile. **Sample data:** **Recipient / employee:** Recipient = To whom it may concern, Employee = Nadia Karim (Sample), Employee ID = VSH-104, Designation = Reporter; **Certificate details:** Purpose = Bank documentation (Sample), Issue date = 25-Nov-2026, Validity = As approved / not assumed.

**Table columns:** —.

**Signatures:** Authorized signatory name/title/signature/date; blank for signing.

**Image:** [Paired screen and print mockup](mockups/07_noc.svg).

### 8. Payment Voucher

**Page:** A4 portrait • **Screen:** Accounting / Vouchers workspace with contextual actions, status and A4 preview. **Print/PDF:** Portrait voucher with payee/bank details, debit line table, total, narration and four signing/acknowledgement slots.

**Header/company:** Embedded VSH logo, VSH NEWS TV and Visionary Baluchistan Media Corporation (Pvt) Ltd; contact and tax details resolve from the company profile. **Sample data:** **Payment details:** Pay to = Bolan Office Supplies (Sample), Pay from = Operating Bank (Sample), Method = Bank transfer, Reference = INV-4451 (Sample).

**Table columns:** Account code, Account title, Particulars, Debit PKR.

**Signatures:** Prepared, checked, approved, and payee acknowledgement; all signature/date lines blank.

**Image:** [Paired screen and print mockup](mockups/08_payment_voucher.svg).

### 9. Receipt Voucher

**Page:** A4 portrait • **Screen:** Accounting / Vouchers workspace with contextual actions, status and A4 preview. **Print/PDF:** Portrait voucher with payer/deposit details, credit line table, total, narration and signing/receipt slots.

**Header/company:** Embedded VSH logo, VSH NEWS TV and Visionary Baluchistan Media Corporation (Pvt) Ltd; contact and tax details resolve from the company profile. **Sample data:** **Receipt details:** Received from = Quetta Media Agency (Sample), Deposit to = Operating Bank (Sample), Method = Bank transfer, Reference = QMA-2026-11 (Sample).

**Table columns:** Account code, Account title, Particulars, Credit PKR.

**Signatures:** Prepared, checked, approved and received-by; signatures remain blank.

**Image:** [Paired screen and print mockup](mockups/09_receipt_voucher.svg).

### 10. Journal Voucher

**Page:** A4 portrait • **Screen:** Accounting / Vouchers workspace with contextual actions, status and A4 preview. **Print/PDF:** Portrait voucher with reference/source, balanced debit-credit lines, totals and narration.

**Header/company:** Embedded VSH logo, VSH NEWS TV and Visionary Baluchistan Media Corporation (Pvt) Ltd; contact and tax details resolve from the company profile. **Sample data:** **Journal details:** Reference = ACCR-NOV-26 (Sample), Period = November 2026, Source = Month-end accrual.

**Table columns:** Account code, Account title, Particulars, Debit PKR, Credit PKR.

**Signatures:** Prepared, reviewed and approved; total debit and credit both PKR 18,500.00.

**Image:** [Paired screen and print mockup](mockups/10_journal_voucher.svg).

### 11. General Ledger

**Page:** A4 landscape • **Screen:** Accounting / Ledgers workspace with contextual actions, status and A4 preview. **Print/PDF:** Landscape transaction ledger with selected period, repeated headings, totals and running balance.

**Header/company:** Embedded VSH logo, VSH NEWS TV and Visionary Baluchistan Media Corporation (Pvt) Ltd; contact and tax details resolve from the company profile. **Sample data:** **Report filters:** Period = 01-Nov-2026 – 25-Nov-2026, Account = All accounts, Basis = Posted entries only.

**Table columns:** Date, Voucher no., Src, Particulars / contra, Debit PKR, Credit PKR, Running bal..

**Signatures:** Optional preparer/reviewer on final page; transaction balances are sample only.

**Image:** [Paired screen and print mockup](mockups/11_general_ledger.svg).

### 12. Account Ledger

**Page:** A4 landscape • **Screen:** Accounting / Ledgers workspace with contextual actions, status and A4 preview. **Print/PDF:** Landscape single-account ledger with opening balance, period transactions and closing balance.

**Header/company:** Embedded VSH logo, VSH NEWS TV and Visionary Baluchistan Media Corporation (Pvt) Ltd; contact and tax details resolve from the company profile. **Sample data:** **Ledger filters:** Account = 1100 · Operating Bank, Period = 01-Nov-2026 – 25-Nov-2026, Status = Posted only.

**Table columns:** Date, Voucher no., Source, Particulars / contra, Debit PKR, Credit PKR, Balance PKR.

**Signatures:** Optional preparer/reviewer; opening/closing balances in this visual are fictional.

**Image:** [Paired screen and print mockup](mockups/12_account_ledger.svg).

### 13. Trial Balance

**Page:** A4 portrait • **Screen:** Accounting / Reports workspace with contextual actions, status and A4 preview. **Print/PDF:** Portrait trial balance with approved six-column heading set, balanced opening/movement/closing totals and final-page sign-off.

**Header/company:** Embedded VSH logo, VSH NEWS TV and Visionary Baluchistan Media Corporation (Pvt) Ltd; contact and tax details resolve from the company profile. **Sample data:** **Report scope:** As of = 25-Nov-2026, Basis = Sample posted balances, Currency = PKR.

**Table columns:** AcCode, Account head title, Opening bal., Total debit, Total credit, Closing bal..

**Signatures:** Prepared, reviewed and approved; blank signature/date lines.

**Image:** [Paired screen and print mockup](mockups/13_trial_balance.svg).

### 14. Employee Master Report

**Page:** A4 landscape • **Screen:** HR / Reports workspace with contextual actions, status and A4 preview. **Print/PDF:** Landscape directory with repeated headings, employee count and privacy-sensitive columns.

**Header/company:** Embedded VSH logo, VSH NEWS TV and Visionary Baluchistan Media Corporation (Pvt) Ltd; contact and tax details resolve from the company profile. **Sample data:** **Report filters:** As of = 25-Nov-2026, Department = All, Status = Active.

**Table columns:** Employee ID, Employee name, Department, Designation, CNIC, Phone, Joined, Salary PKR, Status.

**Signatures:** Optional prepared/reviewed on the final page. CNIC is masked in this review image; salary/CNIC export access must be role-controlled.

**Image:** [Paired screen and print mockup](mockups/14_employee_master_report.svg).

## Review and implementation gates

1. Confirm the screen interaction, authorization, fields and source-of-truth data before implementation; sample values must never be seeded into live company records.
2. Obtain HR approval for every form field, confidentiality rule, recipient and signature role. Appointment, experience, salary, and NOC letters require their approved master wording.
3. Preserve the approved Employee Application DOCX master exactly. Use its existing explicit mapping only; compare final print/PDF output to the master before release.
4. Accounting must approve voucher posting rules, numbering, account treatment, totals and signatories. The balanced voucher and trial-balance values in these images are demonstrative only.
5. Verify A4 print safety, grayscale contrast, long values, pagination, repeating table headings, output permissions and PDF parity before coding is approved.
