from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QToolButton,
    QFormLayout,
    QVBoxLayout,
    QMessageBox,
)

from pathlib import Path

from datetime import date
from decimal import Decimal, InvalidOperation

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDateEdit,
    QFileDialog,
)

from src.app.domain.hr.employee import Employee
from src.app.ui.report_headings import EMPLOYEES_HEADINGS
from src.app.ui.support import (
    call_service,
    create_export_menu,
    export_table,
    fill_table,
)
from src.app.ui.employee_document import (
    EmployeeDocumentError,
    generate_pdf,
    populate_employee_docx,
    preview_employee_pdf,
    print_employee_docx,
)


class EmployeesView(QWidget):
    def __init__(self, services=None, session=None):
        super().__init__()
        self._services = services
        self._last_employee = None

        self.setWindowTitle("Employee Management")

        layout = QVBoxLayout(self)

        title = QLabel("Employee Management")
        title.setStyleSheet(
            "font-size:18px;"
            "font-weight:bold;"
            "padding:10px;"
        )

        layout.addWidget(title)

        form = QFormLayout()

        self.employee_id = QLineEdit()
        self.full_name = QLineEdit()
        self.cnic = QLineEdit()
        self.phone = QLineEdit()
        self.email = QLineEdit()
        self.department = QLineEdit()
        self.designation = QLineEdit()
        self.joining_date = QDateEdit(QDate.currentDate())
        self.joining_date.setCalendarPopup(True)
        self.joining_date.setDisplayFormat("dd-MMM-yyyy")
        self.salary = QLineEdit()
        self.status = QLineEdit()

        form.addRow("Employee ID", self.employee_id)
        form.addRow("Full Name", self.full_name)
        form.addRow("CNIC", self.cnic)
        form.addRow("Phone", self.phone)
        form.addRow("Email", self.email)
        form.addRow("Department", self.department)
        form.addRow("Designation", self.designation)
        form.addRow("Joining Date", self.joining_date)
        form.addRow("Salary", self.salary)
        form.addRow("Status", self.status)

        layout.addLayout(form)

        self.table = QTableWidget()
        fill_table(self.table, EMPLOYEES_HEADINGS, [])
        export = QToolButton()
        export.setText("Export")
        export.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        export.setMenu(create_export_menu(export, self._export))
        layout.addWidget(export)
        layout.addWidget(self.table)

        save_button = QPushButton("Save Employee")
        save_button.clicked.connect(self.save_employee)

        layout.addWidget(save_button)

        document_row = QFormLayout()
        preview_button = QPushButton("Preview Official Form")
        preview_button.clicked.connect(self.preview_official_form)
        docx_button = QPushButton("Save DOCX")
        docx_button.clicked.connect(self.save_official_docx)
        pdf_button = QPushButton("Save PDF")
        pdf_button.clicked.connect(self.save_official_pdf)
        print_button = QPushButton("Print Official Form")
        print_button.clicked.connect(self.print_official_form)
        document_row.addRow(preview_button)
        document_row.addRow(docx_button)
        document_row.addRow(pdf_button)
        document_row.addRow(print_button)
        layout.addLayout(document_row)

    def save_employee(self):
        employee = self._employee_from_form()
        if employee is None:
            return
        if self._services is None or not hasattr(self._services, "employees"):
            self._last_employee = employee
            QMessageBox.information(self, "Employee", "Employee saved successfully.")
            return
        try:
            if self._services.employees.employee_exists(employee.employee_id):
                ok, saved = call_service(
                    self,
                    self._services.employees.update_employee,
                    employee,
                )
            else:
                ok, saved = call_service(
                    self,
                    self._services.employees.create_employee,
                    employee,
                )
        except Exception as ex:
            QMessageBox.critical(self, "Employee", str(ex))
            return
        if ok:
            self._last_employee = saved
            QMessageBox.information(self, "Employee", "Employee saved successfully.")
            self.refresh()

    def _employee_from_form(self):
        joining = self.joining_date.date()
        try:
            salary = Decimal(self.salary.text().strip() or "0")
        except InvalidOperation:
            QMessageBox.warning(self, "Validation Error", "Enter a valid salary.")
            return None
        employee = Employee(
            employee_id=self.employee_id.text().strip(),
            full_name=self.full_name.text().strip(),
            cnic=self.cnic.text().strip(),
            phone=self.phone.text().strip(),
            email=self.email.text().strip(),
            department=self.department.text().strip(),
            designation=self.designation.text().strip(),
            joining_date=date(joining.year(), joining.month(), joining.day()),
            salary=salary,
            status=self.status.text().strip() or "Active",
        )
        try:
            employee.validate()
        except ValueError as ex:
            QMessageBox.warning(self, "Validation Error", str(ex))
            return None
        return employee

    def _last_saved_employee(self):
        employee = getattr(self, "_last_employee", None)
        if employee is not None:
            return employee
        return self._employee_from_form()

    def preview_official_form(self):
        employee = self._last_saved_employee()
        if employee is None:
            return
        try:
            preview_directory = Path.cwd() / "generated" / "employee_forms"
            preview_employee_pdf(employee, preview_directory)
        except EmployeeDocumentError as ex:
            QMessageBox.critical(self, "Official Employee Form", str(ex))

    def save_official_docx(self):
        employee = self._last_saved_employee()
        if employee is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Employee Application Form",
            f"{employee.employee_id}_Employee_Application_Form.docx",
            "Word Document (*.docx)",
        )
        if not path:
            return
        try:
            populate_employee_docx(employee, Path(path))
        except EmployeeDocumentError as ex:
            QMessageBox.critical(self, "Official Employee Form", str(ex))
            return
        QMessageBox.information(self, "Saved", f"Employee application form saved to:\n{path}")

    def save_official_pdf(self):
        employee = self._last_saved_employee()
        if employee is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Employee Application Form PDF",
            f"{employee.employee_id}_Employee_Application_Form.pdf",
            "PDF (*.pdf)",
        )
        if not path:
            return
        try:
            temporary_docx = Path.cwd() / "generated" / "employee_forms" / f"{employee.employee_id}_Employee_Application_Form.docx"
            populate_employee_docx(employee, temporary_docx)
            generate_pdf(temporary_docx, Path(path))
        except (EmployeeDocumentError, OSError) as ex:
            QMessageBox.critical(self, "Official Employee Form", str(ex))
            return
        QMessageBox.information(self, "Saved", f"Employee application form PDF saved to:\n{path}")

    def print_official_form(self):
        employee = self._last_saved_employee()
        if employee is None:
            return
        try:
            temporary_docx = Path.cwd() / "generated" / "employee_forms" / f"{employee.employee_id}_Employee_Application_Form.docx"
            populate_employee_docx(employee, temporary_docx)
            print_employee_docx(temporary_docx)
        except EmployeeDocumentError as ex:
            QMessageBox.critical(self, "Official Employee Form", str(ex))

    def refresh(self):
        if self._services is None or not hasattr(self._services, "employees"):
            fill_table(self.table, EMPLOYEES_HEADINGS, [])
            return
        ok, employees = call_service(self, self._services.employees.list_employees)
        if not ok:
            return
        rows = [
            (
                self._employee_value(employee, "employee_code", "employee_id"),
                self._employee_value(employee, "full_name"),
                self._employee_value(employee, "department"),
                self._employee_value(employee, "designation"),
                self._employee_value(employee, "cnic"),
                self._employee_value(employee, "phone"),
                self._employee_value(employee, "joining_date"),
                self._employee_value(employee, "salary"),
                self._employee_value(employee, "status"),
            )
            for employee in employees
        ]
        fill_table(self.table, EMPLOYEES_HEADINGS, rows, right_cols=(7,))

    @staticmethod
    def _employee_value(employee, key, fallback=None):
        if isinstance(employee, dict):
            return employee.get(key, employee.get(fallback, "") if fallback else "")
        return getattr(employee, key, getattr(employee, fallback, "") if fallback else "")

    def _export(self, file_format: str) -> None:
        rows = [
            tuple(
                self.table.item(row, column).text()
                if self.table.item(row, column) is not None else ""
                for column in range(self.table.columnCount())
            )
            for row in range(self.table.rowCount())
        ]
        export_table(self, "Employees", EMPLOYEES_HEADINGS, rows, file_format)
    