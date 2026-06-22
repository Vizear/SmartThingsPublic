"""
Altantis HUD — Gaming Assistant
Entry point: system tray app that auto-detects important game screen content
and shows a sci-fi HUD notification popup.
"""
import sys
import os
import json
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter, QFont
from PyQt6.QtCore import Qt

from popup import HUDPopup
from monitor import ScreenMonitor
from setup_dialog import SetupDialog

CONFIG_PATH = Path.home() / ".altantis_hud" / "config.json"

# ── Tray icon (drawn in code so we need no image files) ──────────────────────
def _make_icon(size=32) -> QIcon:
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    cyan = QColor("#00d4e8")
    p.setPen(cyan)
    p.setBrush(QColor("#050a14"))
    p.drawRoundedRect(2, 2, size - 4, size - 4, 3, 3)
    p.setPen(QColor("#00e5ff"))
    f = QFont("Consolas", 9, QFont.Weight.Bold)
    p.setFont(f)
    p.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, "HUD")
    p.end()
    return QIcon(px)


# ── Config persistence ────────────────────────────────────────────────────────
def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text())
        except Exception:
            pass
    return {}


def save_config(cfg: dict):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg))


# ── Main Application ──────────────────────────────────────────────────────────
class AltantisHUD(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        self.setQuitOnLastWindowClosed(False)
        self._monitor: ScreenMonitor | None = None
        self._popup: HUDPopup | None = None

        cfg = load_config()
        api_key = cfg.get("api_key", "")

        if not api_key:
            dlg = SetupDialog()
            if dlg.exec() != SetupDialog.DialogCode.Accepted:
                sys.exit(0)
            api_key = dlg.api_key
            save_config({"api_key": api_key})

        self._start(api_key)

    def _start(self, api_key: str):
        self._popup = HUDPopup()

        self._monitor = ScreenMonitor(api_key=api_key, interval=6)
        self._monitor.info_detected.connect(self._on_info)
        self._monitor.start()

        self._tray = QSystemTrayIcon(self)
        self._tray.setIcon(_make_icon())
        self._tray.setToolTip("Altantis HUD — Gaming Assistant")

        menu = QMenu()
        menu.setStyleSheet("""
            QMenu { background: #050a14; color: #7fcfdf; border: 1px solid #005f70;
                    font-family: Consolas, 'Courier New', monospace; font-size: 11px; }
            QMenu::item:selected { background: #005f70; color: #00e5ff; }
        """)
        menu.addAction("Altantis HUD  [running]").setEnabled(False)
        menu.addSeparator()
        test_act = menu.addAction("Test Popup")
        test_act.triggered.connect(self._test_popup)
        menu.addSeparator()
        quit_act = menu.addAction("Exit")
        quit_act.triggered.connect(self._quit)

        self._tray.setContextMenu(menu)
        self._tray.show()

    def _on_info(self, data: dict):
        if self._popup:
            self._popup.show_info(data)
            if self._monitor:
                self._monitor.set_cooldown(15)

    def _test_popup(self):
        """Show a demo popup for testing layout/style."""
        self._on_info({
            "has_info": True,
            "title": "DEMO — DATA CAPTURED",
            "summary": "Test entry from system tray. Real entries appear automatically when important info is detected on screen.",
            "items": [
                {"label": "CODE",     "value": "ALPHA-447-BETA"},
                {"label": "LOCATION", "value": "Sector 7 // Grid B-4"},
                {"label": "NOTE",     "value": "Use at terminal 3 before next checkpoint"},
                {"label": "TIMER",    "value": "02:30 remaining"},
            ],
        })

    def _quit(self):
        if self._monitor:
            self._monitor.stop()
            self._monitor.wait(2000)
        self.quit()


def main():
    app = AltantisHUD()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
