# VSH NEWS TV ERP — Final Visual Design Specification

**Status:** Design blueprint for review before implementation
**Revision:** 1.0
**Date:** 2026-11-25
**Scope:** 26 HR forms and letters, accounting vouchers, operational reports, and ledgers
**Deliverable type:** Screen and print/PDF wireframe specification; not application code or approved legal wording

## 1. Design intent and approval boundary

Establish a single, restrained corporate visual language for VSH NEWS TV ERP. Data-entry screens should be easy to scan and keyboard-operable. Printed and exported documents should use fixed A4 page geometry, repeatable headers and footers, legible tables, and consistent signing areas.

These are functional wireframes, not production templates. The only approved HR document master currently identified is `docs/hr/VSH_Employee_Application_Form.docx`. Its approved wording, page structure, coordinates, styles, and signature areas remain authoritative and immutable; this specification does not replace or rearrange it. The other HR forms and letters require separately supplied/approved masters and, for legally consequential letters, approved wording before they are generated. Do not infer missing payroll, leave, loan, asset, or employee fields from unrelated data.

## 2. Shared design system

### 2.1 Brand and color

| Token | Use | Value |
|---|---|---|
| VSH navy | Main headings, table headings, rules, primary actions | `#17365D` |
| Deep navy | Strong emphasis and secondary heading text | `#102A43` |
| White | Page and form background | `#FFFFFF` |
| Light gray | Section bands, alternating rows, input grouping | `#F1F4F7` |
| Mid gray | Borders, rules, captions, inactive controls | `#AAB4C0` |
| Body text | Labels and values | `#243447` |
| Error/status | Validation or workflow state only | Existing semantic UI colors; never rely on color alone |

Use the navy/white/light-gray palette throughout. Avoid decorative gradients, heavy fills, shadows in print, and color-only distinctions. Printed pages must remain clear in grayscale.

### 2.2 Typography and spacing

- Use the application’s available corporate sans-serif family (fallback: Arial), with embedded/fallback-safe PDF fonts.
- Page title: 16–18 pt bold; section heading: 10–11 pt bold; body: 9.5–10.5 pt; labels/captions: 8–9 pt.
- Screen labels must remain readable at normal desktop scaling; validation text must not be smaller than body text.
- Use a 4 mm base spacing unit. Keep label alignment, field heights, table paddings, and section spacing consistent.
- Use thin navy rules and light-gray section bars. Align currency and numeric values right; dates and identifiers consistently.
- Never truncate a value in print. Wrap long text or move the complete row to the next page.

### 2.3 Fixed A4 page grid

**A4 portrait:** 210 × 297 mm; 12 mm left/right margins; 12 mm top margin; 14 mm bottom margin.
**A4 landscape:** 297 × 210 mm; 12 mm margins on all sides.
**Print-safe content width:** 186 mm portrait; 273 mm landscape.
**Portrait content bands:** header 38 mm; title/metadata 14 mm; body from approximately y=54 mm to y=273 mm; footer begins at y=280 mm.
**Landscape content bands:** header 27 mm; title/metadata 12 mm; body from approximately y=43 mm to y=183 mm; footer begins at y=190 mm.

Use fixed coordinates/grid regions in approved masters rather than flow layouts that change between records. Long reports may use additional pages with the same header and footer; repeat the table heading on every continuation page. Keep totals and signatures with their preceding section; do not split a table row or signature block across pages.

### 2.4 Uniform header, logo, and company information

Every page uses the following shared structure, except the already-approved Employee Application Form, whose master controls its actual header:

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ [VSH LOGO]  VSH NEWS TV                                  DOCUMENT META    │
│             [Company legal name]                          Title / code    │
│             [Address]                                     Date / period   │
│             [Phone]  [Email]  [Website]                   Page x of y    │
│             [Tax/registration no. when relevant]                         │
├──────────────────────────────────────────────────────────────────────────┤
│ Document title / report title                                             │
└──────────────────────────────────────────────────────────────────────────┘
```

- **Logo placement:** upper-left, nominal 22 × 22 mm portrait or 18 × 18 mm landscape; preserve aspect ratio, do not stretch, crop, recolor, or substitute an unapproved mark. Use the configured company logo where available; otherwise use the repository VSH logo asset.
- **Company information:** pull from the company profile, not hard-coded values: legal/display name, address, phone, email, website, and tax/registration number. Show only populated values; preserve alignment when optional values are empty.
- **Document metadata:** document type/code and issue date for forms/letters; reporting period/as-of date for reports/ledgers; voucher number/date/status for vouchers. Page numbering is present on every multipage output.
- Keep a 0.4 mm navy rule under the header. Main title sits below it, left-aligned, in navy.

### 2.5 Uniform footer

```text
────────────────────────────────────────────────────────────────────────────
[Document code or confidential classification]    Generated [date/time]
VSH NEWS TV                                             Page [x] of [y]
```

Use a thin light-gray rule. Footer content is neutral and must not invent a registration/legal statement. Mark payroll, salary certificates, employee evaluation, warning, and other sensitive HR outputs **Confidential** according to the final access policy. Hide generated timestamp if the approved master prohibits it. A footer must never overlap the page body or a handwritten signing area.

### 2.6 Screen and output behavior

- **Screen wireframe:** common application shell with module title, breadcrumb, state indicator (Draft/Saved/Approved/Posted as applicable), and an action strip. Place data-entry fields in grouped cards matching the printed page order. Use inline validation and keyboard navigation. Provide a page preview for printable content without mixing screen-only controls into the output.
- **Print wireframe:** fixed A4 geometry and typography above; no buttons, selection handles, or UI chrome. Use the same field values and ordering as the PDF.
- **PDF export:** must be visually identical to print preview: same page size/orientation, margins, line wraps, pagination, repeating headings, logo, footer, and signature whitespace. No image-only or rasterized text output; text should remain selectable/searchable where the rendering tool permits.
- **Export naming:** suggested filename pattern `[DocumentType]_[RecordOrPeriod]_[YYYYMMDD].pdf`; confirm final naming and retention policy separately.
- **Paper fallback:** blank company profile values do not produce broken placeholders. Missing required business data should be surfaced before generation, not replaced with guessed data.

## 3. Shared ERP screen wireframe

Forms use the same screen shell; the content panels and fields differ by document:

```text
┌ VSH NEWS TV ERP ── HR / Accounting / Reports ────────────────────────────┐
│ [Module title] [Record / period]                         [Draft / Saved]  │
│ [New] [Save draft] [Submit/Approve when applicable] [Preview] [PDF]      │
├──────────────────────────────────────────┬───────────────────────────────┤
│ DATA ENTRY / FILTERS                      │ A4 PAGE PREVIEW               │
│ Section heading                           │ [Header and logo]             │
│ Label      [Field]       Label [Field]    │ [Fixed printable page]        │
│ ...                                        │ [Page x of y]                 │
│ [Validation/help text]                    │                               │
└──────────────────────────────────────────┴───────────────────────────────┘
```

On narrow screens, stack the preview below the form. Do not print the action strip, navigation, validation messages, or unsaved-state indicator. For read-only reports, replace the data-entry column with filters and keep the preview/table as the dominant area.

## 4. HR forms

All new HR form layouts below are conceptual until HR approves their fields and supplies a fixed master. Use the shared header/footer and PDF rules. Keep sensitive data restricted to authorized users and outputs.

### 4.1 Employee Application Form

**Page/orientation:** approved master’s original page count and orientation; do not alter. Existing mapped positions remain authoritative.

```text
┌ APPROVED EMPLOYEE APPLICATION MASTER — LOCKED LAYOUT ─────────────────────┐
│ Existing header, logo and company information exactly as approved         │
│ Personal information: Full name | CNIC | joining date | personal number   │
│ Position & compensation: designation | department | date | salary | ID    │
│ Existing education/reference/employment sections remain as approved       │
│ Existing handwritten fields and all signature blocks remain blank         │
│ Existing footer, page structure, lines, spacing and typography unchanged   │
└───────────────────────────────────────────────────────────────────────────┘
```

- **Screen:** select a saved employee or enter application data in the approved master’s field order; display the immutable page preview. Do not expose template editing controls.
- **Field locations:** use only the existing approved mapping: full name, CNIC, joining date, phone, designation, department, salary, and employee ID at their documented master locations. Email/status remain unmapped unless the master is formally revised and reapproved.
- **Table/signatures:** retain all master tables and leave its handwritten, reference, education, and signature areas untouched.
- **Print/PDF:** use the unchanged approved master geometry; generated copy only. Print and PDF must match the master and preserve all blank signing areas.

### 4.2 Employee Information Form

**Page/orientation:** A4 portrait; one-page summary, with an approved continuation page only if necessary.

```text
┌ EMPLOYEE INFORMATION ───────────── Employee ID [____] ─ Status [______] ┐
│ Identity: Full name [________________]   CNIC [____________________]     │
│ Contact:  Phone [____________________]   Email [___________________]    │
│ Employment: Department [_____________]   Designation [____________]    │
│             Joining date [___________]   Status [__________________]    │
│ Compensation: Salary [____________ PKR]   As-of date [_____________]    │
│ Notes / approved additional information [___________________________]    │
│ Prepared by [____]            Employee acknowledgement [____]            │
└─────────────────────────────────────────────────────────────────────────┘
```

- **Screen fields:** employee ID, name, CNIC, phone, email, department, designation, joining date, salary, and status; visually separate saved data from any future supplemental data.
- **Tables:** none on the standard page. Optional history table only when a reliable history source is approved.
- **Signatures:** prepared/verified and employee acknowledgement; signature labels and requirement need HR approval.
- **Print/PDF:** show the employee identity block prominently; mask CNIC/compensation on derivative or broadly shared versions if access policy requires it.

### 4.3 Leave Application Form

**Page/orientation:** A4 portrait.

```text
┌ LEAVE APPLICATION ─ Application date [____] ─ Request no. [___________] ┐
│ Employee ID [____]  Name [____________]  Department [_______________]   │
│ Leave type [________]  From [________]  To [________]  Days [________]  │
│ Reason / handover notes [____________________________________________]  │
│ Contact during leave [________________]  Balance [source-dependent]     │
│ APPROVAL: Supervisor decision [____]  HR decision [____]  Dates [____]  │
│ Applicant [sign/date]     Supervisor [sign/date]     HR [sign/date]     │
└─────────────────────────────────────────────────────────────────────────┘
```

- **Screen fields:** employee lookup, requested leave type and dates, reason, and contact/handover note. Calculated days and balance are read-only and appear only when backed by approved calendar/leave rules and source data.
- **Tables:** optional compact leave history/entitlement table; not required for the application page.
- **Signatures:** applicant, supervisor, and HR/authorized approver; decision fields remain blank until acted upon.
- **Print/PDF:** include requested dates and decision area on one page; do not imply approval on an unapproved request.

### 4.4 Loan Application Form

**Page/orientation:** A4 portrait; confidential.

```text
┌ EMPLOYEE LOAN APPLICATION ─ Request date [____] ─ Request no. [_______] ┐
│ Employee ID [____]  Name [____________]  Department [_______________]   │
│ Loan purpose [_______________________________________________________]  │
│ Requested amount [PKR ______]  Term [____]  Requested start [_______]  │
│ Proposed instalment [PKR ____]  Repayment source [___________________]  │
│ Supporting notes / attachments [____________________________________]  │
│ Review: eligibility [____]  recommendation [____]  approved amount [__] │
│ Employee [sign/date]     Reviewer [sign/date]     Approver [sign/date]  │
└─────────────────────────────────────────────────────────────────────────┘
```

- **Screen fields:** employee identity, purpose, requested amount/term, requested start date, and supporting-document references. Any instalment calculation or eligibility result must come from an approved policy/calculation source.
- **Tables:** optional repayment schedule, only after terms and calculation rules are approved; clearly label estimates versus approved schedule.
- **Signatures:** applicant, reviewer, authorized approver. No approved amount or repayment promise is prefilled.
- **Print/PDF:** confidential footer; include all approval fields and supporting-document references without embedding unapproved loan terms.

### 4.5 Employee Evaluation Form

**Page/orientation:** A4 portrait; continuation page allowed for narrative and goals.

```text
┌ EMPLOYEE EVALUATION ─ Period [________] ─ Review date [_______________]┐
│ Employee ID [____]  Name [____________]  Department [_______________]   │
│ Role/designation [____________]  Reviewer [_________________________]   │
│ PERFORMANCE DIMENSION       RATING / EVIDENCE / COMMENTS                 │
│ [Dimension 1]               [________________________________________]  │
│ [Dimension 2]               [________________________________________]  │
│ [Dimension 3]               [________________________________________]  │
│ Strengths [____________________] Development goals [________________]   │
│ Employee comments [__________________________________________________]  │
│ Reviewer [sign/date]  Employee acknowledgement [sign/date]  HR [____]  │
└─────────────────────────────────────────────────────────────────────────┘
```

- **Screen fields:** employee/reviewer, evaluation period, approved dimensions and rating scale, evidence/comments, development goals, and acknowledgement.
- **Tables:** rating/evidence/comments table; use a fixed rating legend approved by HR and repeat it on continuation pages.
- **Signatures:** reviewer, employee acknowledgement (not necessarily agreement), and HR/approver where required.
- **Print/PDF:** confidential footer; preserve room for handwritten comments and signatures. Keep long feedback with its rating row.

## 5. HR letters

Letters use A4 portrait and a formal document frame: shared corporate header, document title/metadata, date/reference line, recipient/employee block, body zone, closing, and authorized-signatory block. Body wording must come from an approved master; wireframe prompts below describe data placement only, not legal/disciplinary language. Use confidentiality classification where applicable.

### 5.1 Appointment Letter

**Page map:** Header/logo/company details → issue date and reference → employee name/address/ID block → approved appointment text → position/department/effective date/terms summary if the master contains those fields → acceptance block → authorized signatory.

```text
┌ APPOINTMENT LETTER ─ Ref [________] ─ Issue date [____________________]┐
│ To: [Employee name]  [Address/contact when approved]                     │
│ [Approved master body and terms; no generated legal wording]             │
│ Position [____] Department [____] Effective date [____]                  │
│ Acceptance: Employee signature/date [____]                               │
│ Authorized signatory name/title/signature/date [____________________]   │
└─────────────────────────────────────────────────────────────────────────┘
```

**Screen/fields:** select employee; enter only approved issue/effective dates and terms not sourced from the employee record. **Tables:** none unless the master contains a compensation/terms schedule. **Print/PDF:** identical formal letter page, with acceptance and signatory whitespace.

### 5.2 Confirmation Letter

**Page map:** Header → issue date/reference → employee recipient → approved body → confirmation/effective date and confirmed position if present in master → signatory.

```text
┌ CONFIRMATION LETTER ─ Ref [________] ─ Issue date [___________________]┐
│ To: [Employee name]  Employee ID [____]  Department [_______________]  │
│ [Approved master body]  Effective date [____]  Position [____________] │
│ Authorized signatory name/title/signature/date [____________________]  │
└────────────────────────────────────────────────────────────────────────┘
```

**Screen/fields:** employee, issue/effective dates, and approved source-backed position details. **Tables:** none by default. **Print/PDF:** one-page letter; body wording and footer treatment follow the approved master.

### 5.3 Experience Letter

**Page map:** Header → issue date/reference → employee recipient → approved employment-period/body fields → authorized signatory.

```text
┌ EXPERIENCE LETTER ─ Ref [________] ─ Issue date [_____________________]┐
│ To / recipient [____________________]  Employee ID [________________]  │
│ Name [____________] Designation [________] Department [_____________]  │
│ Employment period: From [____] To [____]  Purpose [if approved]        │
│ [Approved master body]                                                  │
│ Authorized signatory name/title/signature/date [____________________]  │
└────────────────────────────────────────────────────────────────────────┘
```

**Screen/fields:** saved employee and verified employment dates; purpose/recipient only if the master requires it. **Tables:** none. **Print/PDF:** formal single-page certificate; avoid claims beyond verified employment data.

### 5.4 Promotion Letter

**Page map:** Header → issue date/reference → employee block → approved body → current/new role and effective date where approved → signatory.

```text
┌ PROMOTION LETTER ─ Ref [________] ─ Issue date [______________________]┐
│ Employee [____________] ID [____] Department [_______________________]│
│ Current designation [________] New designation [____________________]│
│ Effective date [____] Compensation change [only if approved/source]    │
│ [Approved master body]                                                  │
│ Authorized signatory name/title/signature/date [____________________]  │
└────────────────────────────────────────────────────────────────────────┘
```

**Screen/fields:** employee, approved current/new role, effective date, and any authorized compensation value. **Tables:** optional before/after summary only if the master includes one. **Print/PDF:** keep any compensation details confidential.

### 5.5 Transfer Letter

**Page map:** Header → issue date/reference → employee block → approved body → current/new department, role, location, reporting/effective date fields where present → signatory.

```text
┌ TRANSFER LETTER ─ Ref [________] ─ Issue date [_______________________]┐
│ Employee [____________] ID [____] Current department [_______________]│
│ New department [________] Role [________] Location [_______________]  │
│ Reporting to [____________] Effective date [_________________________]│
│ [Approved master body]                                                  │
│ Authorized signatory name/title/signature/date [____________________]  │
└────────────────────────────────────────────────────────────────────────┘
```

**Screen/fields:** employee, verified current assignment, approved new assignment, and effective date. **Tables:** none. **Print/PDF:** fit formal body and acceptance/acknowledgement field if the master requires one.

### 5.6 Warning Letter

**Page map:** Header → issue date/reference and confidential indicator → employee block → approved master text/incident fields → response deadline if approved → authorized signatory and acknowledgement.

```text
┌ WARNING LETTER — CONFIDENTIAL ─ Ref [____] ─ Date [__________________]┐
│ To: [Employee] ID [____] Department [________]                        │
│ Incident reference/date [________] Response deadline [_____________]  │
│ [Approved master wording only]                                         │
│ Authorized signatory [sign/date] Employee acknowledgement [sign/date] │
└───────────────────────────────────────────────────────────────────────┘
```

**Screen/fields:** restrict access; use approved incident metadata and deadline. **Tables:** none by default. **Print/PDF:** confidential footer; do not expose in general employee reports or uncontrolled exports.

### 5.7 Salary Certificate

**Page map:** Header → issue date/reference → certificate title → employee identity and verified salary/as-of period → approved certification body → authorized signatory.

```text
┌ SALARY CERTIFICATE ─ Ref [________] ─ Issue date [___________________]┐
│ Employee [____________] ID [____] Designation [_____________________]│
│ Department [________] Salary [PKR ______] As-of/period [___________] │
│ [Approved master certification wording and recipient/purpose if used] │
│ Authorized signatory name/title/signature/date [___________________] │
└──────────────────────────────────────────────────────────────────────┘
```

**Screen/fields:** selected employee, verified compensation and as-of date, recipient/purpose only if approved. **Tables:** none. **Print/PDF:** confidential; make currency and period explicit; do not imply payroll-period history if only current salary is available.

### 5.8 NOC

**Page map:** Header → issue date/reference → recipient/employee block → purpose/validity fields if approved → approved master body → authorized signatory.

```text
┌ NO OBJECTION CERTIFICATE ─ Ref [____] ─ Issue date [_________________]┐
│ To/recipient [____________________] Employee [______________________]│
│ Employee ID [____] Designation [________] Department [_____________] │
│ Purpose [________] Valid until [________] (only if master requires)  │
│ [Approved master wording]                                             │
│ Authorized signatory name/title/signature/date [___________________]│
└─────────────────────────────────────────────────────────────────────┘
```

**Screen/fields:** employee and approved purpose/recipient/validity values. **Tables:** none. **Print/PDF:** formal single-page certificate; wording and any validity clause must be approved.

### 5.9 Relieving Letter

**Page map:** Header → issue date/reference → employee block → verified separation/last-working-day fields → approved body → clearance/signatory fields if master includes them.

```text
┌ RELIEVING LETTER ─ Ref [________] ─ Issue date [_____________________]┐
│ Employee [____________] ID [____] Department [______________________]│
│ Designation [________] Last working day [____] Separation ref [____] │
│ [Approved master body]                                                 │
│ Authorized signatory name/title/signature/date [___________________] │
└──────────────────────────────────────────────────────────────────────┘
```

**Screen/fields:** employee, verified last working day, approved separation reference. **Tables:** clearance checklist only if part of the approved master. **Print/PDF:** one-page formal letter; do not infer clearance or settlement status.

## 6. Accounting vouchers

Voucher pages are A4 portrait. Use a dark-navy title band, voucher number/date/status metadata, party/account details, a ruled line table, totals, narration, and compact signature row. The line table header repeats if a voucher continues. Amounts are right-aligned and displayed to two decimal places; currency label is explicit. Do not show a posted state until the accounting workflow confirms it.

### 6.1 Payment Voucher

```text
┌ PAYMENT VOUCHER ─ No. [____] ─ Date [____] ─ Status [Draft/Posted] ┐
│ Pay to [________________]  Pay-from cash/bank account [___________] │
│ Payment method [____]  Cheque/ref [____]  Payee reference [______] │
│ ACCOUNT CODE | ACCOUNT TITLE | PARTICULARS | DEBIT (PKR)             │
│ [__________] | [___________] | [_________] | [____________]          │
│ ...                                                               │
│ Narration [_____________________________________________________]  │
│ Total [PKR __________]  Amount in words [if approved]              │
│ Prepared [sign]  Checked [sign]  Approved [sign]  Paid/Received [sign]│
└────────────────────────────────────────────────────────────────────┘
```

**Screen fields:** payment date, payee, cash/bank account, method/reference, line accounts/particulars/debits, narration. **Table:** account code/title, particulars, debit; system-derived balancing credit/cash-bank line as dictated by approved posting design. **Signatures:** prepared, checked, approved, payee acknowledgement. **Print/PDF:** no screen controls; totals remain with last line and signatures.

### 6.2 Receipt Voucher

```text
┌ RECEIPT VOUCHER ─ No. [____] ─ Date [____] ─ Status [Draft/Posted] ┐
│ Received from [____________]  Deposit-to cash/bank [_____________] │
│ Receipt method [____]  Cheque/ref [____]  Payer reference [______]│
│ ACCOUNT CODE | ACCOUNT TITLE | PARTICULARS | CREDIT (PKR)           │
│ [__________] | [___________] | [_________] | [____________]          │
│ ...                                                               │
│ Narration [_____________________________________________________]  │
│ Total [PKR __________]  Amount in words [if approved]              │
│ Prepared [sign]  Checked [sign]  Approved [sign]  Received by [sign]│
└────────────────────────────────────────────────────────────────────┘
```

**Screen fields:** receipt date, payer, deposit account, method/reference, credited account lines, narration. **Table:** account code/title, particulars, credit; balancing cash/bank debit follows approved posting rules. **Signatures:** prepared, checked, approved, payer acknowledgement. **Print/PDF:** same fixed voucher page with repeated table heading when needed.

### 6.3 Journal Voucher

```text
┌ JOURNAL VOUCHER ─ No. [____] ─ Date [____] ─ Status [Draft/Posted] ┐
│ Reference [________]  Source [________]  Period [_______________]  │
│ ACCOUNT CODE | ACCOUNT TITLE | PARTICULARS | DEBIT | CREDIT         │
│ [__________] | [___________] | [_________] | [___] | [_____]        │
│ ...                                                               │
│ Total debit [PKR ____]                 Total credit [PKR ____]      │
│ Narration / business purpose [___________________________________]  │
│ Prepared [sign]  Reviewed [sign]  Approved [sign]                   │
└────────────────────────────────────────────────────────────────────┘
```

**Screen fields:** date, reference/source, account lines, debit/credit, narration. **Table:** both debit and credit per line; validate equality before posting. **Signatures:** preparer, reviewer, approver. **Print/PDF:** show both totals together and keep approval block on the final page.

### 6.4 Contra Voucher

```text
┌ CONTRA VOUCHER ─ No. [____] ─ Date [____] ─ Status [Draft/Posted] ┐
│ Transfer from cash/bank [____________] To cash/bank [____________]│
│ Instrument/reference [________]  Value date [___________________] │
│ ACCOUNT CODE | ACCOUNT TITLE | PARTICULARS | DEBIT | CREDIT        │
│ [__________] | [___________] | [_________] | [___] | [_____]       │
│ Transfer amount [PKR ______]  Narration [_______________________] │
│ Prepared [sign]  Checked [sign]  Approved [sign]                   │
└───────────────────────────────────────────────────────────────────┘
```

**Screen fields:** transfer date, source/destination cash-bank accounts, instrument/reference, amount, narration. **Table:** source/destination ledger lines with balanced debit/credit. **Signatures:** prepared, checked, approved. **Print/PDF:** compact, one-page layout; prohibit non-cash/bank accounts according to the approved contra workflow.

## 7. Reports

Reports are read-only outputs with a filter strip on screen and a frozen parameter summary below the title in print. Use alternating light-gray rows, repeated column headings, right-aligned numeric values, clear totals, and no signature area on every page. On the final page, reserve prepared-by/reviewed-by signoff only when the report is intended as an authorized formal report. Report selection filters stay on-screen; the chosen period/as-of date prints.

### 7.1 Employee Master Report

**Page/orientation:** A4 landscape; confidential; repeat headings.

```text
┌ EMPLOYEE MASTER REPORT ─ As of [date] ─ Department [filter/all] ─────┐
│ EMPLOYEE ID | NAME | DEPARTMENT | DESIGNATION | CNIC* | PHONE | JOINED│
│ [_________] | [__] | [_________] | [_________] | [___] | [___] | [__]│
│ ...                                                                │
│ Footer totals: Employee count [__]          Prepared / reviewed [___]│
└─────────────────────────────────────────────────────────────────────┘
```

**Screen fields:** search and filters for department/status/date as available; table sortable by approved columns. **Table:** employee ID, name, department, designation, CNIC (masked/omitted by access policy), phone, joining date, salary/status only for authorized users. **Signatures:** optional prepared/reviewed on last page. **Print/PDF:** landscape; repeat header; label filtered scope; protect sensitive columns in preview/export as well as print.

### 7.2 Department Report

**Page/orientation:** A4 portrait; landscape if approved detailed employee columns exceed the safe width.

```text
┌ DEPARTMENT REPORT ─ As of [date] ─ Status [filter/all] ──────────────┐
│ DEPARTMENT | ACTIVE EMPLOYEES | INACTIVE EMPLOYEES | TOTAL           │
│ [_________] | [_____________] | [_______________] | [____]          │
│ [Department subtotal/detail rows]                                    │
│ Overall total [____]                Prepared / reviewed [________]   │
└─────────────────────────────────────────────────────────────────────┘
```

**Screen fields:** as-of date and active/status filter. **Table:** department, active count, inactive count, total; optional employee detail expansion on screen, printed only when explicitly selected. **Signatures:** optional report signoff on final page. **Print/PDF:** one department per subtotal group; do not invent department heads or budgets absent from source data.

### 7.3 Payroll Report

**Page/orientation:** A4 landscape; confidential.

```text
┌ PAYROLL REPORT ─ Period [month/year] ─ Department [filter/all] ─────┐
│ EMPLOYEE ID | NAME | DEPARTMENT | GROSS* | DEDUCTIONS* | NET*        │
│ [_________] | [__] | [_________] | [____] | [_________] | [___]      │
│ ...                                                                │
│ Totals: Gross [____] Deductions [____] Net [____]                    │
│ Prepared [sign]  Reviewed [sign]  Authorized [sign]                  │
└─────────────────────────────────────────────────────────────────────┘
```

**Screen fields:** payroll period, department, status, and approval state only when backed by an implemented payroll source. **Table:** employee ID/name/department and approved gross, deduction, net components; detailed components require policy and data-model approval. **Signatures:** preparer, reviewer, authorizer on final page. **Print/PDF:** confidential marking, landscape, repeated table head, grand totals only after all pages, page totals distinguished from grand totals. A mockup does not imply payroll calculation is currently available.

### 7.4 Asset Report

**Page/orientation:** A4 landscape; source-module-dependent.

```text
┌ ASSET REPORT ─ As of [date] ─ Category [filter/all] ────────────────┐
│ ASSET ID | DESCRIPTION | CATEGORY | LOCATION | STATUS | COST/BOOK*  │
│ [______] | [_________] | [______] | [______] | [____] | [________] │
│ ...                                                                │
│ Count [__]  Total value [source/policy-dependent]  Reviewed [____]  │
└─────────────────────────────────────────────────────────────────────┘
```

**Screen fields:** as-of date, category, location, status. **Table:** asset identifier, description, category, location, status, acquisition date and cost/book value only if the approved asset source provides them. **Signatures:** optional prepared/reviewed signoff. **Print/PDF:** landscape, repeated columns, no fabricated depreciation or valuation. Asset-module availability and data definitions must be confirmed before implementation.

## 8. Ledgers and account directory

Ledger pages are read-only. Screen filters sit above the result grid; print includes the selected account/date range/as-of date. Long ledgers use landscape orientation, repeat column headings and carry forward balances clearly. Numeric columns are right-aligned. Opening/closing values must be sourced from accounting calculations; do not use blank or guessed amounts as zero.

### 8.1 General Ledger

**Page/orientation:** A4 landscape.

```text
┌ GENERAL LEDGER ─ Period [from–to] ─ Account [all] ────────────────┐
│ DATE | VOUCHER NO | SRC | PARTICULARS / CONTRA | DEBIT | CREDIT | RUNNING BAL│
│ [__] | [________] | [_] | [__________________] | [___] | [____] | [_________]│
│ ...                                                               │
│ Opening [source-backed]  Period totals [____/____]  Closing [____]│
│ Prepared / reviewed [________________]                             │
└───────────────────────────────────────────────────────────────────┘
```

**Screen fields:** from/to dates, account, source, voucher status. **Table:** retain approved headings: Date, Voucher No, Src, Particulars / Contra, Debit, Credit, Running Bal. **Signatures:** optional prepared/reviewed on final page. **Print/PDF:** landscape, account/date scope below title, repeating headings and brought-forward balance per page.

### 8.2 Account Ledger

**Page/orientation:** A4 landscape, one selected account at a time.

```text
┌ ACCOUNT LEDGER ─ [Account code] [Account title] ─ Period [from–to] ┐
│ DATE | VOUCHER NO | SOURCE | PARTICULARS / CONTRA | DEBIT | CREDIT | BALANCE│
│ [__] | [________] | [_____] | [__________________] | [___] | [____] | [_____]│
│ ...                                                               │
│ Opening balance [source-backed]     Closing balance [source-backed]│
│ Prepared / reviewed [________________]                              │
└────────────────────────────────────────────────────────────────────┘
```

**Screen fields:** required account selector, from/to date, posted/unposted status. **Table:** date, voucher number, source, particulars/contra, debit, credit, running balance. **Signatures:** optional preparer/reviewer. **Print/PDF:** same ledger rhythm as General Ledger, with account title/code repeated on continuation pages.

### 8.3 Trial Balance

**Page/orientation:** A4 portrait; switch to landscape only if approved chart/account titles cannot fit.

```text
┌ TRIAL BALANCE ─ As of [date] ─ Basis [approved accounting basis] ──┐
│ AC CODE | ACCOUNT HEAD TITLE | OPENING BAL | TOTAL DEBIT | TOTAL CREDIT | CLOSING BAL│
│ [_____] | [_______________] | [__________] | [_________] | [__________] | [__________]│
│ ...                                                                │
│ TOTALS: Opening [D/C]  Debit [____]  Credit [____]  Closing [D/C]   │
│ Prepared [sign]  Reviewed [sign]  Approved [sign]                  │
└────────────────────────────────────────────────────────────────────┘
```

**Screen fields:** as-of date and approved account/zero-balance filters. **Table:** retain the approved headings: AcCode, Account Head Title, Opening Bal, Total Debit, Total Credit, Closing Bal. **Signatures:** preparer, reviewer, approver on final page. **Print/PDF:** repeat headings; totals reconcile according to approved accounting rules. If a data source does not supply an opening balance, display “not available” or omit the column only after report-owner approval—never silently imply zero.

### 8.4 Chart of Accounts

**Page/orientation:** A4 portrait.

```text
┌ CHART OF ACCOUNTS ─ As of [date] ─ Status [active/all] ────────────┐
│ AC CODE | ACCOUNT NAME | TYPE | OPENING BALANCE | CURRENT BALANCE | ACTIVE│
│ [_____] | [__________] | [__] | [______________] | [_____________] | [___]│
│ ...                                                                │
│ Account count [__]       Prepared / reviewed [________________]    │
└────────────────────────────────────────────────────────────────────┘
```

**Screen fields:** code/name search, account type, active status. **Table:** preserve approved headings: AcCode, AcName, TypeCode, Opening Balance, Current Balance, Active. **Signatures:** optional prepared/reviewed on final page. **Print/PDF:** indent account hierarchy consistently, repeat headings, and leave balances blank or exclude them if the source does not provide them; do not fabricate figures.

## 9. Deliverable layout matrix

| Deliverable | Default page | Primary data location | Table | Signature area | Output note |
|---|---|---|---|---|---|
| Employee Application Form | Approved master | Existing approved field coordinates | Master-defined | Existing master-defined, unchanged | Immutable master |
| Employee Information Form | Portrait | Identity/contact/employment blocks | Optional history | Prepared/employee acknowledgement | Mask sensitive values by policy |
| Leave Application Form | Portrait | Employee and leave request blocks | Optional history | Applicant/supervisor/HR | Approval state must be explicit |
| Loan Application Form | Portrait | Employee, purpose, requested terms | Optional schedule | Applicant/reviewer/approver | Confidential; terms require policy |
| Employee Evaluation Form | Portrait | Employee/reviewer and period | Ratings/evidence | Reviewer/employee/HR | Confidential; continuation page |
| Appointment Letter | Portrait | Recipient and approved terms | Master-dependent | Authorized signatory/acceptance | Approved wording required |
| Confirmation Letter | Portrait | Employee and effective date | None by default | Authorized signatory | Approved master required |
| Experience Letter | Portrait | Employment identity/period | None | Authorized signatory | Verified dates only |
| Promotion Letter | Portrait | Current/new role and effective date | Optional before/after | Authorized signatory | Compensation is restricted |
| Transfer Letter | Portrait | Current/new assignment | None | Authorized signatory/acknowledgement | Approved master required |
| Warning Letter | Portrait | Confidential recipient/incident metadata | None | Authorized signatory/acknowledgement | Approved wording and access control |
| Salary Certificate | Portrait | Employee and salary-as-of block | None | Authorized signatory | Confidential |
| NOC | Portrait | Recipient/purpose/validity | None | Authorized signatory | Approved wording required |
| Relieving Letter | Portrait | Employee and last-working-day block | Optional clearance | Authorized signatory | Do not infer clearance |
| Payment Voucher | Portrait | Party and payment details | Account debit lines | Prepared/checked/approved/payee | Fixed totals/signing row |
| Receipt Voucher | Portrait | Payer and deposit details | Account credit lines | Prepared/checked/approved/payer | Fixed totals/signing row |
| Journal Voucher | Portrait | Reference and posting state | Debit/credit lines | Prepared/reviewed/approved | Balanced totals |
| Contra Voucher | Portrait | Cash/bank transfer endpoints | Balanced account lines | Prepared/checked/approved | Cash/bank only |
| Employee Master Report | Landscape | Filter summary | Employee rows | Optional final-page review | Confidential columns |
| Department Report | Portrait | As-of/filter summary | Department counts | Optional final-page review | No assumed department head |
| Payroll Report | Landscape | Payroll period/filter | Payroll values | Prepared/reviewed/authorized | Confidential, source-dependent |
| Asset Report | Landscape | As-of/filter summary | Asset rows | Optional final-page review | Asset source must exist |
| General Ledger | Landscape | Period/account scope | Ledger transactions | Optional final-page review | Carry forward per page |
| Account Ledger | Landscape | Account and period | Account transactions | Optional final-page review | One account per output |
| Trial Balance | Portrait | As-of date/basis | Account balances | Prepared/reviewed/approved | Reconcile totals |
| Chart of Accounts | Portrait | As-of/status scope | Account hierarchy | Optional final-page review | No unsupported balances |

## 10. Screen-to-print field and pagination rules

1. Use one field label and value format across screen, print, and PDF. Hide screen-only actions from print.
2. Print the reporting period, as-of date, employee identity, voucher number, or account scope needed to interpret the output.
3. Keep employee identifiers stable and visible; apply masking/omission to CNIC, salary, and payroll values by role and export permission.
4. Repeat column headings on every continuation page. Add “continued” context for multi-page voucher/report sections where needed.
5. Keep totals, signature labels, and their related content together. Do not place a grand total at the bottom of an earlier page than its final detail row.
6. Use explicit empty states in the ERP screen. For an empty printed report, show “No records for the selected criteria” with the selected period rather than an unexplained blank page.
7. Leave all handwritten signature/date fields blank in generated documents. Never synthesize a signature image or claim approval from a user’s typed name.
8. For forms or letters awaiting approved masters, show a screen status of “Template pending approval”; do not export an improvised legal document as final.

## 11. Pre-implementation review checklist

- [ ] HR approves fields, field sources, sensitivity classification, and signature roles for each HR form.
- [ ] HR/legal/authorized management supplies and approves each formal letter’s wording and fixed master.
- [ ] Accounting approves voucher fields, posting signs, totals, numbering, and authorized signature roles.
- [ ] Report owners approve column sets, filters, totals, zero/blank behavior, and confidential export policy.
- [ ] Ledger/report values are traced to a verified source and calculation rule; unavailable values are not invented.
- [ ] Company profile confirms legal name, address, contact values, registration number, and approved logo.
- [ ] Print samples are reviewed on A4 portrait/landscape printers and grayscale; PDF is compared page-for-page with print preview.
- [ ] Page breaks, repeating headers, footer clearance, Unicode/font fallback, long values, and empty datasets are reviewed.
- [ ] Fixed masters are versioned and hash-checked; populated copies must never modify their source masters.
