import os
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from src.app.application.session import Session
from src.app.domain.security import permissions as P
from src.app.ui import vouchers_view
from src.app.ui.vouchers_view import VouchersView


def test_print_preview_opens_the_approved_pdf_output(monkeypatch):
    app = QApplication.instance() or QApplication([])
    selected = SimpleNamespace(
        id=1, voucher_no="PV-2026-000001", narration="Monthly wages", status="Draft"
    )
    detail = SimpleNamespace(header=selected, lines=[])
    services = SimpleNamespace(
        vouchers=SimpleNamespace(get_voucher=lambda session, voucher_id: detail),
        accounts=SimpleNamespace(),
        company=SimpleNamespace(get_profile=lambda session: SimpleNamespace()),
    )
    view = VouchersView(
        services,
        Session(1, "voucher-test", frozenset({P.VOUCHER_VIEW})),
    )
    view._rows = [selected]
    view.table.addItem(selected.voucher_no)
    view.table.setCurrentRow(0)
    view._selected_detail = [("5400000005", "Salaries", "November salary", 100, 100)]
    generated = {}

    def generate(voucher, company, output_path):
        output_path = Path(output_path)
        output_path.write_bytes(b"approved-layout-pdf")
        generated["path"] = output_path

    view._voucher_pdf.generate = generate
    opened = []
    monkeypatch.setattr(
        vouchers_view,
        "QDesktopServices",
        SimpleNamespace(openUrl=lambda url: opened.append(url) or True),
    )

    try:
        view._export("print")
        preview_path = generated["path"]
        assert preview_path.suffix == ".pdf"
        assert preview_path.read_bytes() == b"approved-layout-pdf"
        assert len(opened) == 1
        assert view._preview_file is not None
    finally:
        if view._preview_file is not None:
            view._preview_file.remove()
        view.close()
        app.processEvents()
