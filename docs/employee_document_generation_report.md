# Employee official document generation

## Workflow

The employee screen provides:

1. Employee data entry and save/update.
2. Generate/preview the approved application form.
3. Save a populated DOCX copy.
4. Save a populated PDF copy.
5. Print the populated form.

Save occurs before document generation. A saved or currently entered employee
value supplies the official form data. The application never creates or edits
the master template.

## DOCX generation

`src/app/ui/employee_document.py` copies
`docs/hr/VSH_Employee_Application_Form.docx` to a destination, reads the copy's
ZIP package, and inserts text only in the mapped `w:t` data cells within
`word/document.xml`. It uses namespace-preserving `lxml` XML editing and retains
all other package parts, header/footer XML, styles, relationships, section
properties, page content, and signature areas.

The resulting 5-page metadata and master package structure are retained.
Generated DOCX verification is performed through document/package inspection
and Microsoft Word PDF conversion.

## Preview

Preview generates a temporary official DOCX and converts it to PDF using
Microsoft Word automation on Windows. The PDF is opened through the Windows
default PDF application.

## PDF and print

- **Save PDF:** creates a populated DOCX, invokes Word's
  `ExportAsFixedFormat`, and saves the selected PDF destination.
- **Print:** creates a populated DOCX and invokes Word `PrintOut`.
- **Save DOCX:** saves a copy of the populated DOCX at the selected destination.

Both PDF and print require Microsoft Word and Windows COM automation.

## Employee data persistence

The Employee Entry form now supplies a joining date and saves the department
through the employee repository. Existing employee records are updated when
their employee ID already exists; otherwise a new employee is created.

## Verification

- 22 unit tests pass, including approved-template population and signature-cell
  checks.
- A verification DOCX was generated successfully and has a valid Word package.
- Microsoft Word successfully generated a verification PDF from the populated
  DOCX.
- The master template hash remained unchanged.
