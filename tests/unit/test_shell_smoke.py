import os
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from src.app.application.session import Session
from src.app.main import Shell


def test_shell_shows_dashboard_with_fake_services():
    app = QApplication.instance() or QApplication([])
    shell = Shell(SimpleNamespace(auth=object()))
    session = Session(1, "smoke-test", frozenset())

    try:
        shell.login.authenticated.emit(session)
        app.processEvents()

        assert shell._main.isVisible()
        assert shell._main._stack.currentWidget() is shell._main._dashboard
        assert shell._main._dashboard.isVisible()
    finally:
        shell.shutdown()
