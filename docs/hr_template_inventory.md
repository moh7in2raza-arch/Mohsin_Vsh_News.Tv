# HR Document Center template inventory

## Status

The approved Employee Application Form at
`docs/hr/VSH_Employee_Application_Form.docx` is the only HR master currently
present in the repository. It is not a master for any item below. No approved
masters, field-location maps, or document-specific wording have been supplied
for these 16 document types. All entries are therefore **Pending approved
DOCX master** and are not yet available for generation.

Each row lists the data expected to be mapped if the approved master contains a
corresponding field. It is an implementation checklist, not proposed legal
wording or confirmation that the master contains those fields.

## Common autofill data

The center should use the existing employee and company profile services. Map
only fields present in the selected master.

| Source | Available values |
|---|---|
| Employee | Employee ID, full name, CNIC, phone, email, department, designation, joining date, salary, status |
| Company profile | Company name, address, phone, email, website, logo path, tax/registration number |

Values not available from these sources (such as a decision, event date,
reason, or clearance sign-off) must be explicitly supplied or retrieved from a
trusted existing source. Do not infer them.

## Per-document inventory

| # | Document | Fixed master (expected path) | Candidate document-specific values beyond common autofill | Status |
|---:|---|---|---|---|
| 1 | Appointment Letter | `docs/hr/Appointment_Letter.docx` | Issue date, appointment/effective date, employment type, probation terms, work location, reporting details, approved compensation/benefits terms | Pending approved DOCX master |
| 2 | Offer Letter | `docs/hr/Offer_Letter.docx` | Issue date, offer expiry, proposed start date, offered designation/department, offered compensation, acceptance deadline/conditions | Pending approved DOCX master |
| 3 | Employment Contract | `docs/hr/Employment_Contract.docx` | Contract start/end dates, employment terms and conditions, compensation terms, work location, applicable authorized signatories | Pending approved DOCX master |
| 4 | Salary Certificate | `docs/hr/Salary_Certificate.docx` | Issue date, salary period/as-of date, authorized signatory | Pending approved DOCX master |
| 5 | Experience Certificate | `docs/hr/Experience_Certificate.docx` | Issue date, employment end date, experience period, purpose if required, authorized signatory | Pending approved DOCX master |
| 6 | NOC Certificate | `docs/hr/NOC_Certificate.docx` | Issue date, NOC purpose/recipient if required, validity period, authorized signatory | Pending approved DOCX master |
| 7 | Leave Approval Letter | `docs/hr/Leave_Approval_Letter.docx` | Leave type, start/end dates, number of days, approval date, approver | Pending approved DOCX master |
| 8 | Promotion Letter | `docs/hr/Promotion_Letter.docx` | Issue/effective date, new designation/department, revised compensation if approved, approving authority | Pending approved DOCX master |
| 9 | Increment Letter | `docs/hr/Increment_Letter.docx` | Issue/effective date, previous and revised compensation, increment amount/percentage if approved, approving authority | Pending approved DOCX master |
| 10 | Transfer Letter | `docs/hr/Transfer_Letter.docx` | Issue/effective date, current and new department/designation/location, reporting details, approving authority | Pending approved DOCX master |
| 11 | Warning Letter | `docs/hr/Warning_Letter.docx` | Issue date, incident/date and approved description, response or corrective-action deadline, authorized signatory | Pending approved DOCX master |
| 12 | Show Cause Notice | `docs/hr/Show_Cause_Notice.docx` | Issue date, approved allegation/grounds, response deadline, inquiry/contact details, authorized signatory | Pending approved DOCX master |
| 13 | Termination Letter | `docs/hr/Termination_Letter.docx` | Issue/effective date, approved reason/category, notice/separation terms, authorized signatory | Pending approved DOCX master |
| 14 | Resignation Acceptance Letter | `docs/hr/Resignation_Acceptance_Letter.docx` | Issue date, resignation date, accepted last working day/effective date, authorized signatory | Pending approved DOCX master |
| 15 | Relieving Letter | `docs/hr/Relieving_Letter.docx` | Issue date, last working day, approved separation reference, authorized signatory | Pending approved DOCX master |
| 16 | Clearance Form | `docs/hr/Clearance_Form.docx` | Clearance departments/items, clearance decisions and dates, responsible persons/signatures, final approval | Pending approved DOCX master |

The expected filenames above are provisional conventions only. Use the actual
approved filenames supplied for implementation and update the registry and
inventory accordingly.

## Master intake checklist

For each document, obtain a separately approved DOCX master and confirm:

- The final approved wording, layout, branding, and page structure.
- Which employee and company fields may be populated, and exact locations.
- Which document-specific fields are required and their authoritative source.
- Which signature, approval, and handwritten areas must remain blank.
- Whether a master revision replaces an earlier version and who approves the
  updated field map.

Do not create a replacement master or runtime layout while this information is
pending. Register a document for preview, DOCX, PDF, and print only after its
master and mapping pass the package-preservation and field-population checks
described in [`hr_document_center_design.md`](hr_document_center_design.md).
