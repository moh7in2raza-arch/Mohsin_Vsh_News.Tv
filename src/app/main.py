import logging
import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from src.app.bootstrap import build_services, start_logging
from src.app.ui.login_window import LoginWindow
from src.app.ui.main_window import VshNewsMainWindow
from src.app.ui.style import apply_style

log = logging.getLogger(__name__)


class Shell:
    """Owns the top-level windows: login <-> main."""

    def __init__(self, services):
        self._services = services
        self._main = None
        self.login = LoginWindow(services.auth)
        self.login.authenticated.connect(self._open_main)

    def start(self) -> None:
        self.login.reset()
        self.login.show()

    def _open_main(self, session) -> None:
        self._main = VshNewsMainWindow(self._services, session)
        self._main.logged_out.connect(self.start)
        self._main.show()
        self.login.hide()


def _excepthook(exc_type, exc, tb) -> None:
    log.critical("Unhandled error", exc_info=(exc_type, exc, tb))
    QMessageBox.critical(None, "Unexpected error",
                         "The application hit an unexpected error. Details were written to the log.")


def main() -> int:
    start_logging()
    sys.excepthook = _excepthook
    app = QApplication(sys.argv)
    apply_style(app)
    shell = Shell(build_services())
    shell.start()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

