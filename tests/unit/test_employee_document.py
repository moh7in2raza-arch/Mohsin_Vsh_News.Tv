from datetime import date
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from src.app.domain.hr.employee import Employee
from src.app.ui.employee_document import (
    MASTER_TEMPLATE,
    PERSONAL_NAME,
    CNIC,
    JOINING_DATE_PERSONAL,
    PHONE,
    POSITION_DESIGNATION,
    POSITION_DEPARTMENT,
    POSITION_JOINING_DATE,
    POSITION_SALARY,
    POSITION_EMPLOYEE_ID,
    SIGNATURE_CELLS,
    populate_employee_docx,
)


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _cell_text(document_xml: bytes, table_index, row_index, cell_index) -> str:
    root = ET.fromstring(document_xml)
    tables = root.findall(f".//{{{W_NS}}}body/{{{W_NS}}}tbl")
    row = tables[table_index].findall(f"{{{W_NS}}}tr")[row_index]
    cell = row.findall(f"{{{W_NS}}}tc")[cell_index]
    return "".join(text.text or "" for text in cell.findall(".//{%s}t" % W_NS))


def test_populate_employee_docx_preserves_master_and_signature_cells(tmp_path):
    master_before = sha256(MASTER_TEMPLATE.read_bytes()).hexdigest()
    employee = Employee(
        employee_id="VSH-104",
        full_name="Test Employee",
        cnic="12345-6789012-3",
        phone="0300-1234567",
        email="test@example.com",
        department="News",
        designation="Reporter",
        joining_date=date(2026, 11, 24),
        salary=Decimal("125000.00"),
        status="Active",
    )
    output = tmp_path / "VSH-104_Employee_Application_Form.docx"
    populate_employee_docx(employee, output)

    assert sha256(MASTER_TEMPLATE.read_bytes()).hexdigest() == master_before
    assert output.is_file()

    with ZipFile(output) as generated:
        assert generated.testzip() is None
        document_xml = generated.read("word/document.xml")
        for name in generated.namelist():
            if name != "word/document.xml":
                with ZipFile(MASTER_TEMPLATE) as master:
                    assert generated.read(name) == master.read(name)

    assert _cell_text(document_xml, *PERSONAL_NAME).endswith("Test Employee")
    assert _cell_text(document_xml, *CNIC) == "12345-6789012-3"
    assert _cell_text(document_xml, *JOINING_DATE_PERSONAL) == "24-Nov-2026"
    assert _cell_text(document_xml, *PHONE) == "0300-1234567"
    assert _cell_text(document_xml, *POSITION_DESIGNATION) == "Reporter"
    assert _cell_text(document_xml, *POSITION_DEPARTMENT) == "News"
    assert _cell_text(document_xml, *POSITION_JOINING_DATE) == "24-Nov-2026"
    assert _cell_text(document_xml, *POSITION_SALARY) == "125,000.00"
    assert _cell_text(document_xml, *POSITION_EMPLOYEE_ID) == "VSH-104"

    for table_index, row_index, cell_index in SIGNATURE_CELLS:
        assert _cell_text(
            document_xml, table_index, row_index, cell_index
        ) == ""
