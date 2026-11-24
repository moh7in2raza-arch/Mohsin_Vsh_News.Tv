# Employee application form field mapping

## Immutable master

The fixed master is:

`docs/hr/VSH_Employee_Application_Form.docx`

Its approved SHA-256 is
`34BBF0CE77B45982230795198800BDE49DE4371937A92727874CF5A9C906FE27`.

The master is copied unchanged for every output. The implementation modifies
only named employee-data cells in the copied document package and does not edit
headers, footers, section properties, page breaks, wording, colors, layout,
styles, or signature cells.

## Mapped employee fields

| Master location | Employee value |
|---|---|
| Personal Information: Applicant's Full Name | `full_name` |
| Personal Information: CNIC Number | `cnic` |
| Personal Information: Date of Joining | `joining_date` formatted `dd-Mmm-yyyy` |
| Personal Information: Personal Number | `phone` |
| Position & Compensation: Position / Designation | `designation` |
| Position & Compensation: Department | `department` |
| Position & Compensation: Date of Joining | `joining_date` formatted `dd-Mmm-yyyy` |
| Position & Compensation: Monthly Salary (PKR) | `salary` formatted with two decimals and thousands separators |
| Position & Compensation: Employee ID | `employee_id` |

The following employee fields remain outside the approved form mapping:

- Email
- Gender
- Marital status
- Alternate number
- Residential address
- Status

They are not inserted because the master has no corresponding approved
employee-data position for these values.

## Blank fields

The education, reference, previous-job, employment-type, duty-timing,
probation, office-location, administrator, checklist, and other unconnected
areas remain blank. The two-column Full Name / Signature areas at table indices
8, 12, 17, 19, and 22 remain blank. These include all identified signature
blocks for physical signing.

## Package verification

A generated verification copy was checked against the master. Every package
part except `word/document.xml` is byte-identical. The master file hash remains
unchanged. The generated copy opened successfully in Microsoft Word for PDF
conversion; signature-cell and non-mapped employee fields remained blank.
