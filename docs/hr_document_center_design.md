# HR Document Center design

## Status and scope

The center will provide a single workflow for the 16 document types listed in
[`hr_template_inventory.md`](hr_template_inventory.md). Every document must be
populated from its own approved, fixed DOCX master. The master controls wording,
layout, pagination, branding, and signature areas.

The repository currently contains only the approved Employee Application Form
master at `docs/hr/VSH_Employee_Application_Form.docx`. It does not contain
approved masters for the HR Document Center documents. Implementation of
document-specific mappings and generation is therefore blocked until those
masters are supplied and approved. Do not copy, repurpose, or treat the
application form as a master for another document.

## Existing architecture to follow

The approved employee form workflow is documented in
[`employee_document_generation_report.md`](employee_document_generation_report.md)
and implemented in `src/app/ui/employee_document.py`:

1. The source DOCX is a fixed master and is never edited.
2. Generation copies the master and updates only explicitly mapped employee
   data cells in the copied `word/document.xml`.
3. The rest of the DOCX package, including styles, relationships,
   headers/footers, page setup, and signature areas, is preserved.
4. Preview creates a populated DOCX, converts it to PDF with Microsoft Word
   automation, and opens that PDF.
5. PDF export and printing use the same Word automation path.

The HR Document Center should reuse this fixed-master approach and the existing
PDF/print helpers (`generate_pdf` and `print_employee_docx`). It must not build
document layouts, wording, or page structure from Python/Qt at runtime.

## Target workflow

1. The user selects an employee and one of the 16 document types.
2. The center loads the saved employee record and current company profile.
3. The document-specific form requests only values not held by the employee or
   company profile (for example, an offer expiry date or a clearance decision).
4. The selected document's registered approved master is copied to an output
   DOCX. Its explicit field map populates only approved data positions.
5. The user can preview the result, save DOCX, save PDF, or print it.

Employee and company values should be sourced from the existing employee and
company services, not duplicated in the center. The existing company profile
contains company name, address, phone, email, website, logo path, and tax
number. Insert only values for which the selected approved master has an
explicit mapped field. Do not alter master text or fill signature/approval
blocks.

## Template registry and mapping contract

Maintain one registry entry per document type. Each entry must identify:

- Stable document key, display name, and master path.
- Master version or SHA-256 used for change detection.
- Explicit mappings from employee/company/document-specific data to approved
  locations in that master.
- Required fields, optional fields, and intentionally blank signature or
  approval locations.

Use the supplied approved master as the source of truth when establishing
field locations. Follow the existing explicit cell-coordinate mapping pattern
where the master uses tables. Do not infer fields from visual position at
runtime, perform broad text substitutions, or fall back to another document's
master. A missing master or invalid mapping must produce a visible error; it
must not generate a success-shaped blank or improvised document.

Keep masters under `docs/hr/` (or a dedicated subdirectory beneath it) with
stable, descriptive filenames. Generated files belong under
`generated/hr_documents/`, never beside or over a master. Each generated file
must be a separate copy. A changed master should trigger a deliberate mapping
review and corresponding test updates.

## Document-specific values

The employee and company profile provide common identity and contact fields.
Document-specific values (such as effective dates, reasons, amounts, approval
decisions, and clearance sign-offs) must be explicit inputs or come from a
trusted existing service. They must not be guessed from unrelated employee
fields. Required values must be validated before generation; missing values
must be clearly reported to the user.

Document text that can have contractual, disciplinary, or employment-law
impact must come from an approved master. Operators may enter only the
document-specific data defined for that master; the center must not generate
or rewrite legal clauses.

## Output actions

| Action | Behavior |
|---|---|
| Preview | Populate a temporary DOCX from the selected master, convert to PDF, and open the PDF. |
| Generate DOCX | Save a populated copy of the selected master at a user-selected path. |
| Generate PDF | Populate a temporary DOCX and export it through Microsoft Word automation to a user-selected path. |
| Print | Populate a temporary DOCX and send it to the configured printer through Microsoft Word automation. |

These operations must be available for each document after that document's
approved master and mapping are registered. They require Windows and Microsoft
Word under the existing implementation. Failures to locate a master, populate
it, convert it, open a preview, or print must be shown as errors.

## Validation requirements

For every registered master:

- Assert that the master hash is unchanged by all output actions.
- Verify that the generated DOCX is a valid ZIP/OOXML package.
- Verify populated values at their mapped locations.
- Verify that unmapped content, package parts, page layout, and signature or
  approval blocks remain unchanged.
- Test missing required values, missing master files, and invalid mappings.
- Verify PDF conversion, preview, and print integration where Windows/Word is
  available; unit tests should not require Word automation.

Until approved masters are supplied, keep the 16 inventory entries explicitly
marked as awaiting an approved master. Do not present an unavailable document
as generatable.
