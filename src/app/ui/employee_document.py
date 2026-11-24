from __future__ import annotations

import copy
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML_NS = "http://www.w3.org/XML/1998/namespace"
MASTER_TEMPLATE = Path(__file__).resolve().parents[3] / "docs" / "hr" / "VSH_Employee_Application_Form.docx"

# Body table indices and cell positions are tied to the immutable approved master.
PERSONAL_NAME = (1, 0, 0)
CNIC = (1, 1, 1)
JOINING_DATE_PERSONAL = (1, 2, 1)
PHONE = (1, 4, 1)
POSITION_DESIGNATION = (15, 0, 1)
POSITION_DEPARTMENT = (15, 0, 3)
POSITION_JOINING_DATE = (15, 2, 3)
POSITION_SALARY = (15, 3, 1)
POSITION_EMPLOYEE_ID = (15, 5, 3)

SIGNATURE_CELLS = (
    (8, 1, 0), (8, 1, 1),
    (12, 1, 0), (12, 1, 1),
    (17, 1, 0), (17, 1, 1),
    (19, 1, 0), (19, 1, 1),
    (22, 1, 0), (22, 1, 1),
)


class EmployeeDocumentError(RuntimeError):
    pass


def employee_mapping(employee) -> dict[tuple[int, int, int], str]:
    joining = getattr(employee, "joining_date", None)
    return {
        PERSONAL_NAME: getattr(employee, "full_name", "") or "",
        CNIC: getattr(employee, "cnic", "") or "",
        JOINING_DATE_PERSONAL: joining.strftime("%d-%b-%Y") if joining else "",
        PHONE: getattr(employee, "phone", "") or "",
        POSITION_DESIGNATION: getattr(employee, "designation", "") or "",
        POSITION_DEPARTMENT: getattr(employee, "department", "") or "",
        POSITION_JOINING_DATE: joining.strftime("%d-%b-%Y") if joining else "",
        POSITION_SALARY: f"{float(getattr(employee, 'salary', 0) or 0):,.2f}",
        POSITION_EMPLOYEE_ID: getattr(employee, "employee_id", "") or "",
    }


def _set_cell_text(cell, value: str) -> None:
    paragraphs = cell.findall(f"{{{W_NS}}}p")
    if not paragraphs:
        paragraph = etree.SubElement(cell, f"{{{W_NS}}}p")
    else:
        paragraph = paragraphs[-1]

    if not value:
        return

    run = etree.SubElement(paragraph, f"{{{W_NS}}}r")
    text = etree.SubElement(run, f"{{{W_NS}}}t")
    text.set(f"{{{XML_NS}}}space", "preserve")
    text.text = str(value)


def populate_employee_docx(employee, destination: Path) -> Path:
    if not MASTER_TEMPLATE.is_file():
        raise EmployeeDocumentError(f"Approved employee form not found: {MASTER_TEMPLATE}")

    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(MASTER_TEMPLATE, destination)

    temporary_dir = Path(tempfile.mkdtemp(prefix="vsh_employee_form_"))
    try:
        with ZipFile(MASTER_TEMPLATE, "r") as source:
            document_xml = source.read("word/document.xml")

        parser = etree.XMLParser(remove_blank_text=False)
        root = etree.fromstring(document_xml, parser)
        tables = root.findall(f".//{{{W_NS}}}body/{{{W_NS}}}tbl")
        mapping = employee_mapping(employee)

        for (table_index, row_index, cell_index), value in mapping.items():
            rows = tables[table_index].findall(f"{{{W_NS}}}tr")
            cells = rows[row_index].findall(f"{{{W_NS}}}tc")
            _set_cell_text(cells[cell_index], value)

        updated_document = etree.tostring(
            root,
            encoding="UTF-8",
            xml_declaration=True,
        )

        with ZipFile(destination, "r") as existing:
            replacements = {
                name: existing.read(name)
                for name in existing.namelist()
            }
        replacements["word/document.xml"] = updated_document

        rebuilt = temporary_dir / "rebuilt.docx"
        with ZipFile(rebuilt, "w", ZIP_DEFLATED) as output:
            for name, payload in replacements.items():
                output.writestr(name, payload)
        shutil.move(str(rebuilt), str(destination))
    finally:
        shutil.rmtree(temporary_dir, ignore_errors=True)

    return destination


def _word_script(input_docx: Path, output_pdf: Path | None = None, print_document: bool = False) -> str:
    input_literal = str(input_docx).replace("'", "''")
    output_literal = str(output_pdf).replace("'", "''") if output_pdf is not None else ""
    operations = []
    if output_pdf is not None:
        operations.append(
            "$doc.ExportAsFixedFormat("
            f"'{output_literal}', 17, $false, 0, 0, 0, 0, 7, $true, $true, 0, $true)"
        )
    if print_document:
        operations.append("$doc.PrintOut([Type]::Missing, [Type]::Missing, [Type]::Missing, "
                           "[Type]::Missing, [Type]::Missing, [Type]::Missing, "
                           "[Type]::Missing, [Type]::Missing, [Type]::Missing, "
                           "[Type]::Missing, [Type]::Missing, [Type]::Missing)")
    return (
        "$ErrorActionPreference='Stop'; "
        "$word=$null; $doc=$null; "
        "try { "
        "$word=New-Object -ComObject Word.Application; "
        "$word.Visible=$false; "
        f"$doc=$word.Documents.Open('{input_literal}', $false, $true); "
        + "; ".join(operations)
        + "; } finally { "
        "if ($doc -ne $null) { $doc.Close($false) }; "
        "if ($word -ne $null) { $word.Quit() }; "
        "if ($doc -ne $null) { [Runtime.InteropServices.Marshal]::ReleaseComObject($doc) | Out-Null }; "
        "if ($word -ne $null) { [Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null }; "
        "}"
    )


def generate_pdf(input_docx: Path, output_pdf: Path) -> Path:
    output_pdf = Path(output_pdf)
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    if sys.platform != "win32":
        raise EmployeeDocumentError("Microsoft Word PDF conversion is only available on Windows")
    powershell = shutil.which("powershell.exe") or shutil.which("powershell")
    if powershell is None:
        raise EmployeeDocumentError("PowerShell/Word automation is unavailable")
    result = subprocess.run(
        [powershell, "-NoProfile", "-STA", "-Command", _word_script(input_docx, output_pdf)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not output_pdf.is_file():
        detail = (result.stderr or result.stdout or "Word PDF conversion failed").strip()
        raise EmployeeDocumentError(detail)
    return output_pdf


def print_employee_docx(input_docx: Path) -> None:
    if sys.platform != "win32":
        raise EmployeeDocumentError("Microsoft Word printing is only available on Windows")
    powershell = shutil.which("powershell.exe") or shutil.which("powershell")
    if powershell is None:
        raise EmployeeDocumentError("PowerShell/Word automation is unavailable")
    result = subprocess.run(
        [powershell, "-NoProfile", "-STA", "-Command", _word_script(input_docx, print_document=True)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "Word print failed").strip()
        raise EmployeeDocumentError(detail)


def preview_employee_pdf(employee, directory: Path) -> Path:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    employee_id = str(getattr(employee, "employee_id", "employee")).strip() or "employee"
    docx_path = directory / f"{employee_id}_Employee_Application_Form.docx"
    pdf_path = directory / f"{employee_id}_Employee_Application_Form.pdf"
    populate_employee_docx(employee, docx_path)
    generate_pdf(docx_path, pdf_path)
    if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(pdf_path))):
        raise EmployeeDocumentError("The generated PDF could not be opened for preview")
    return pdf_path
