"""Colours, fonts and the one stylesheet for the main window (UI layer only, ADR-001)."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QColor

# src/app/ui/theme.py -> project root is three levels up from this folder
ROOT = Path(__file__).resolve().parents[3]
RESOURCES = ROOT / "resources"
ICON_DIR = RESOURCES / "icons"        # optional: <key>.svg replaces the built-in glyph
LOGO_FILE = RESOURCES / "logo.png"    # company logo, used in header, banner and print later

NAVY = "#0B2E6B"
NAVY_DEEP = "#071F4A"
ACTIVE_BLUE = "#1E6FE0"
RED = "#E3242B"
PAGE_BG = "#F3F6FB"
TEXT = "#14213D"
MUTED = "#5B6B85"

FONT = "Segoe UI"
GLYPH_FONT = "Segoe UI Emoji"


def rgba(hex_color: str, alpha: int) -> str:
    c = QColor(hex_color)
    return f"rgba({c.red()},{c.green()},{c.blue()},{alpha})"


APP_QSS = f"""
QMainWindow {{ background: {PAGE_BG}; }}
QWidget#page {{ background: {PAGE_BG}; }}

/* ---------- header ---------- */
QFrame#header {{ background: {NAVY}; border-bottom: 3px solid {RED}; }}
QLabel#headerTitle {{ color: white; font-size: 36px; font-weight: 800; }}
QLabel#headerSub {{ color: #DCE6F7; font-size: 17px; }}
QLabel#headerUserName {{ color: white; font-size: 15px; font-weight: 700; }}
QLabel#headerUser {{ color: #DCE6F7; font-size: 13px; }}
QLabel#headerClock {{ color: white; font-size: 15px; }}
QFrame#headerDivider {{ background: rgba(255,255,255,70); }}

/* ---------- sidebar ---------- */
QFrame#sidebar {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {NAVY}, stop:1 {NAVY_DEEP});
}}
QPushButton#sideBtn {{
    background: transparent; border: none;
    border-bottom: 1px solid rgba(255,255,255,28); text-align: left;
}}
QPushButton#sideBtn:hover {{ background: rgba(255,255,255,26); }}
QPushButton#sideBtn:checked {{ background: {ACTIVE_BLUE}; }}
QPushButton#sideBtn QLabel#navTitle {{ color: white; font-size: 15px; font-weight: 600; background: transparent; }}
QPushButton#sideBtn QLabel#navChevron {{ color: white; font-size: 20px; background: transparent; }}

/* ---------- banner ---------- */
QFrame#banner {{
    border: 1px solid #D5E0F0; border-radius: 10px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFFFFF, stop:1 #CFE0F7);
}}
QLabel#bannerWelcome {{ color: {NAVY}; font-size: 24px; font-weight: 600; background: transparent; }}
QLabel#bannerName {{ color: {NAVY}; font-size: 46px; font-weight: 800; background: transparent; }}
QLabel#bannerSub {{ color: {TEXT}; font-size: 20px; background: transparent; }}
QLabel#bannerTag {{ color: {ACTIVE_BLUE}; font-size: 19px; font-style: italic; background: transparent; }}

/* ---------- category cards ---------- */
QLabel#cardTitle {{ color: {TEXT}; font-size: 19px; font-weight: 700; background: transparent; }}
QPushButton#rowBtn {{ background: transparent; border: none; border-radius: 6px; text-align: left; }}
QPushButton#rowBtn:hover {{ background: rgba(20,33,61,14); }}
QPushButton#rowBtn QLabel#navTitle {{ color: {TEXT}; font-size: 15px; background: transparent; }}
QPushButton#rowBtn QLabel#navChevron {{ color: {MUTED}; font-size: 20px; background: transparent; }}

/* ---------- opened screens ---------- */
QPushButton#backBtn {{
    background: white; border: 1px solid #C9D4E6; border-radius: 6px;
    padding: 7px 16px; color: {NAVY}; font-weight: 600;
}}
QPushButton#backBtn:hover {{ background: #E8F0FC; }}
QLabel#screenTitle {{ color: {NAVY}; font-size: 24px; font-weight: 700; }}
QLabel#placeholder {{ color: {MUTED}; font-size: 17px; background: white; border: 1px dashed #C9D4E6; border-radius: 10px; }}

/* ---------- status bar ---------- */
QFrame#statusBar {{ background: {NAVY}; }}
QFrame#statusBar QLabel {{ color: white; font-size: 13px; background: transparent; }}
QLabel#statusTag {{ font-style: italic; }}

/* ---------- popup menus from the sidebar ---------- */
QMenu {{ background: white; border: 1px solid #C9D4E6; padding: 6px; }}
QMenu::item {{ padding: 8px 30px 8px 14px; color: {TEXT}; font-size: 14px; }}
QMenu::item:selected {{ background: {ACTIVE_BLUE}; color: white; }}
QMenu::item:disabled {{ color: #9AA5B5; }}
"""
