"""Reusable widgets for the main window. UI only: no SQL, no repositories (ADR-001)."""
from __future__ import annotations

from datetime import datetime
from typing import Callable

from PySide6.QtCore import QPoint, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QFrame, QGraphicsOpacityEffect, QGridLayout, QHBoxLayout, QLabel,
    QMenu, QPushButton, QVBoxLayout, QWidget,
)

from src.app.ui import theme
from src.app.ui.navigation import (
    CATEGORIES, CATEGORY_BY_KEY, SIDEBAR, Category, UserInfo,
)

Can = Callable[[str], bool]


# ---------------------------------------------------------------- small pieces
class LogoBadge(QLabel):
    """Company logo from resources/logo.png, or a red NEWS badge until the file exists."""

    def __init__(self, size: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if theme.LOGO_FILE.exists():
            pm = QPixmap(str(theme.LOGO_FILE)).scaled(
                size, size, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            self.setPixmap(pm)
        else:
            self.setText("VSH\nNEWS")
            self.setStyleSheet(
                f"background:{theme.RED}; color:#FFD400; font-weight:800; "
                f"font-size:{max(10, size // 5)}px; border-radius:{size // 8}px;")


class IconBadge(QLabel):
    """A logo for one menu entry: resources/icons/<key>.svg if present, else a glyph."""

    def __init__(self, key: str, glyph: str, size: int, glyph_pt: int, *,
                 bg: str | None = None, fg: str = "white",
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        svg = theme.ICON_DIR / f"{key}.svg"
        if svg.exists():
            inner = int(size * (0.55 if bg else 1.0))
            self.setPixmap(QIcon(str(svg)).pixmap(QSize(inner, inner)))
        else:
            self.setText(glyph)
            self.setFont(QFont(theme.GLYPH_FONT, glyph_pt))
        radius = size // 2 if bg else 0
        self.setStyleSheet(
            f"background:{bg or 'transparent'}; color:{fg}; border-radius:{radius}px;")


class NavButton(QPushButton):
    """One clickable row: logo, title, optional chevron. Used by sidebar and cards."""

    def __init__(self, key: str, glyph: str, title: str, *, name: str,
                 icon_px: int, icon_fg: str, height: int = 40,
                 chevron: bool = True, enabled: bool = True,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName(name)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(height)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 2, 12, 2)
        lay.setSpacing(12)
        parts: list[QWidget] = [IconBadge(key, glyph, icon_px, 12, fg=icon_fg)]
        label = QLabel(title)
        label.setObjectName("navTitle")
        lay.addWidget(parts[0])
        lay.addWidget(label, 1)
        parts.append(label)
        if chevron:
            arrow = QLabel("›")
            arrow.setObjectName("navChevron")
            lay.addWidget(arrow)
            parts.append(arrow)
        for w in parts:                       # clicks go to the button, not the labels
            w.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        if not enabled:
            self.setEnabled(False)
            self.setToolTip("You do not have permission")
            fade = QGraphicsOpacityEffect(self)
            fade.setOpacity(0.4)
            self.setGraphicsEffect(fade)


# ---------------------------------------------------------------- header
class HeaderBar(QFrame):
    def __init__(self, user: UserInfo, company: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("header")
        self.setFixedHeight(104)
        row = QHBoxLayout(self)
        row.setContentsMargins(24, 8, 24, 8)
        row.setSpacing(16)

        row.addWidget(LogoBadge(82))
        titles = QVBoxLayout()
        titles.setSpacing(0)
        titles.addStretch(1)
        t = QLabel("VSH NEWS TV")
        t.setObjectName("headerTitle")
        s = QLabel(company)
        s.setObjectName("headerSub")
        titles.addWidget(t)
        titles.addWidget(s)
        titles.addStretch(1)
        row.addLayout(titles)
        row.addStretch(1)

        row.addWidget(IconBadge("user", "👤", 56, 22, bg=theme.ACTIVE_BLUE))
        info = QVBoxLayout()
        info.setSpacing(1)
        info.addStretch(1)
        name = QLabel(user.full_name)
        name.setObjectName("headerUserName")
        info.addWidget(name)
        for text in (f"User ID: {user.user_id}", f"Role: {user.role}"):
            lab = QLabel(text)
            lab.setObjectName("headerUser")
            info.addWidget(lab)
        info.addStretch(1)
        row.addLayout(info)

        div = QFrame()
        div.setObjectName("headerDivider")
        div.setFixedSize(1, 56)
        row.addWidget(div)

        row.addWidget(IconBadge("clock", "🕒", 36, 18, fg="white"))
        clock = QVBoxLayout()
        clock.setSpacing(1)
        clock.addStretch(1)
        self._time = QLabel()
        self._date = QLabel()
        for lab in (self._time, self._date):
            lab.setObjectName("headerClock")
            clock.addWidget(lab)
        clock.addStretch(1)
        row.addLayout(clock)

        self._tick()
        timer = QTimer(self)
        timer.timeout.connect(self._tick)
        timer.start(1000)

    def _tick(self) -> None:
        now = datetime.now()
        self._time.setText(now.strftime("%I:%M:%S %p"))
        self._date.setText(now.strftime("%d-%b-%Y"))


# ---------------------------------------------------------------- sidebar
class Sidebar(QFrame):
    homeRequested = Signal()
    itemRequested = Signal(str)
    exitRequested = Signal()

    def __init__(self, can: Can, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(250)
        self._can = can
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 14, 0, 0)
        lay.setSpacing(0)

        self._home_btn: NavButton | None = None
        for entry in SIDEBAR:
            btn = NavButton(entry.key, entry.glyph, entry.title, name="sideBtn",
                            icon_px=28, icon_fg="white", height=54,
                            chevron=bool(entry.category_keys))
            if entry.key == "home":
                btn.setCheckable(True)
                btn.setChecked(True)
                btn.clicked.connect(lambda _=False: self.homeRequested.emit())
                self._home_btn = btn
            elif entry.key == "exit":
                btn.clicked.connect(lambda _=False: self.exitRequested.emit())
            else:
                btn.clicked.connect(lambda _=False, e=entry, b=btn: self._popup(b, e.category_keys))
            lay.addWidget(btn)

        lay.addStretch(1)
        art = IconBadge("sidebar_art", "📡", 130, 64, fg="white")
        lay.addWidget(art, alignment=Qt.AlignmentFlag.AlignHCenter)
        lay.addSpacing(24)

    def set_home_active(self, active: bool) -> None:
        if self._home_btn is not None:
            self._home_btn.setChecked(active)

    def _popup(self, button: QWidget, category_keys: tuple[str, ...]) -> None:
        menu = QMenu(self)
        for ckey in category_keys:
            for item in CATEGORY_BY_KEY[ckey].items:
                act = menu.addAction(f"{item.glyph}   {item.title}")
                act.setEnabled(item.permission is None or self._can(item.permission))
                act.triggered.connect(lambda _=False, k=item.key: self.itemRequested.emit(k))
        menu.exec(button.mapToGlobal(QPoint(button.width(), 0)))


# ---------------------------------------------------------------- home page
class WelcomeBanner(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("banner")
        self.setFixedHeight(190)
        row = QHBoxLayout(self)
        row.setContentsMargins(30, 14, 30, 14)
        row.setSpacing(34)
        row.addWidget(LogoBadge(150))

        col = QVBoxLayout()
        col.setSpacing(0)
        col.addStretch(1)
        for text, name in (
            ("Welcome to", "bannerWelcome"),
            ("VSH NEWS TV", "bannerName"),
            ("Integrated Management System", "bannerSub"),
            ("Efficient   •   Transparent   •   Reliable", "bannerTag"),
        ):
            lab = QLabel(text)
            lab.setObjectName(name)
            col.addWidget(lab)
        col.addStretch(1)
        row.addLayout(col)
        row.addStretch(1)

        art_file = theme.RESOURCES / "banner.png"      # optional artwork for the right side
        if art_file.exists():
            art = QLabel()
            art.setPixmap(QPixmap(str(art_file)).scaledToHeight(
                160, Qt.TransformationMode.SmoothTransformation))
            art.setStyleSheet("background:transparent;")
            row.addWidget(art)
        else:
            row.addWidget(IconBadge("banner", "📡", 150, 66, fg=theme.ACTIVE_BLUE))


class CategoryCard(QFrame):
    requested = Signal(str)

    def __init__(self, cat: Category, can: Can, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet(
            f"QFrame#card {{ background:{theme.rgba(cat.color, 16)}; "
            f"border:1px solid {theme.rgba(cat.color, 70)}; "
            f"border-bottom:4px solid {cat.color}; border-radius:10px; }}")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 14, 14, 10)
        lay.setSpacing(4)

        head = QHBoxLayout()
        head.setSpacing(14)
        head.addWidget(IconBadge(f"cat_{cat.key}", cat.glyph, 58, 22, bg=cat.color))
        title = QLabel(cat.title)
        title.setObjectName("cardTitle")
        title.setWordWrap(True)
        head.addWidget(title, 1)
        lay.addLayout(head)
        lay.addSpacing(8)

        for item in cat.items:
            allowed = item.permission is None or can(item.permission)
            row = NavButton(item.key, item.glyph, item.title, name="rowBtn",
                            icon_px=26, icon_fg=cat.color, height=36,
                            chevron=cat.key != "exit", enabled=allowed)
            row.clicked.connect(lambda _=False, k=item.key: self.requested.emit(k))
            lay.addWidget(row)
        lay.addStretch(1)


class HomePage(QWidget):
    requested = Signal(str)

    def __init__(self, can: Can, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("page")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(26, 22, 26, 22)
        lay.setSpacing(22)
        lay.addWidget(WelcomeBanner())

        grid = QGridLayout()
        grid.setSpacing(18)
        for i, cat in enumerate(CATEGORIES):
            card = CategoryCard(cat, can)
            card.requested.connect(self.requested)
            grid.addWidget(card, i // 4, i % 4)
        for c in range(4):
            grid.setColumnStretch(c, 1)
        for r in range(2):
            grid.setRowStretch(r, 1)
        lay.addLayout(grid, 1)


# ---------------------------------------------------------------- opened screens
class ScreenFrame(QWidget):
    """Wraps any form: a Home button and the screen title above it."""
    backRequested = Signal()

    def __init__(self, title: str, body: QWidget, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("page")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(26, 18, 26, 18)
        lay.setSpacing(14)
        top = QHBoxLayout()
        back = QPushButton("←  Home")
        back.setObjectName("backBtn")
        back.setCursor(Qt.CursorShape.PointingHandCursor)
        back.clicked.connect(lambda _=False: self.backRequested.emit())
        heading = QLabel(title)
        heading.setObjectName("screenTitle")
        top.addWidget(back)
        top.addSpacing(12)
        top.addWidget(heading)
        top.addStretch(1)
        lay.addLayout(top)
        lay.addWidget(body, 1)


def placeholder(message: str) -> QLabel:
    lab = QLabel(message)
    lab.setObjectName("placeholder")
    lab.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lab.setWordWrap(True)
    return lab


# ---------------------------------------------------------------- status bar
class StatusBar(QFrame):
    def __init__(self, db_label: str, db_ok: bool, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("statusBar")
        self.setFixedHeight(40)
        row = QHBoxLayout(self)
        row.setContentsMargins(20, 0, 20, 0)
        row.setSpacing(10)
        self._dot = QLabel()
        self._dot.setFixedSize(16, 16)
        self._text = QLabel()
        row.addWidget(self._dot)
        row.addWidget(self._text)
        row.addStretch(1)
        row.addWidget(QLabel("🛡  System Ready"))
        row.addStretch(1)
        tag = QLabel("VSH NEWS TV  –  Working for a Better Tomorrow")
        tag.setObjectName("statusTag")
        row.addWidget(tag)
        self.set_database(db_ok, db_label)

    def set_database(self, ok: bool, label: str) -> None:
        self._dot.setStyleSheet(
            f"background:{'#2ECC40' if ok else theme.RED}; border-radius:8px;")
        self._text.setText(f"Database: {'Connected' if ok else 'Disconnected'} ({label})")
