"""HUD-style notification popup with 10-second auto-close."""
import random
import string
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QRect, pyqtProperty
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QFont, QFontDatabase,
    QLinearGradient, QPainterPath,
)

# ── Colour palette ────────────────────────────────────────────────────────────
BG_DEEP   = "#050a14"
BG_PANEL  = "#080f1e"
CYAN_DIM  = "#005f70"
CYAN_MID  = "#00aac0"
CYAN_BRIGHT = "#00d4e8"
CYAN_GLOW   = "#00e5ff"
GREEN_DATA  = "#39ff80"
AMBER       = "#ffb800"
TEXT_DIM    = "#4a8a98"
TEXT_MID    = "#7fcfdf"
TEXT_BRIGHT = "#c8f0f8"

AUTO_CLOSE_MS = 10_000   # 10 seconds
TICK_MS       = 50


def _rand_hex(n=8):
    return "".join(random.choices("0123456789ABCDEF", k=n))


def _rand_id():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


# ── Corner-decoration painter ─────────────────────────────────────────────────
class CornerFrame(QWidget):
    """Draws the angular sci-fi border with corner brackets."""

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        cs = 18   # corner size
        inset = 1

        # Outer glow
        glow = QPen(QColor(CYAN_MID), 1)
        glow.setStyle(Qt.PenStyle.SolidLine)
        p.setPen(glow)
        p.drawRect(inset, inset, w - 2 * inset - 1, h - 2 * inset - 1)

        # Inner bright border
        p.setPen(QPen(QColor(CYAN_BRIGHT), 1.5))
        path = QPainterPath()
        # Top-left corner
        path.moveTo(inset + cs, inset)
        path.lineTo(inset, inset)
        path.lineTo(inset, inset + cs)
        # Bottom-left corner
        path.moveTo(inset, h - inset - cs)
        path.lineTo(inset, h - inset)
        path.lineTo(inset + cs, h - inset)
        # Top-right corner
        path.moveTo(w - inset - cs, inset)
        path.lineTo(w - inset, inset)
        path.lineTo(w - inset, inset + cs)
        # Bottom-right corner
        path.moveTo(w - inset, h - inset - cs)
        path.lineTo(w - inset, h - inset)
        path.lineTo(w - inset - cs, h - inset)
        p.drawPath(path)

        # Corner tick marks
        p.setPen(QPen(QColor(CYAN_GLOW), 2))
        tick = 6
        for x, y, dx, dy in [
            (inset, inset + cs + 4, 0, tick),
            (inset + cs + 4, inset, tick, 0),
            (w - inset, inset + cs + 4, 0, tick),
            (w - inset - cs - 4, inset, -tick, 0),
            (inset, h - inset - cs - 4, 0, -tick),
            (inset + cs + 4, h - inset, tick, 0),
            (w - inset, h - inset - cs - 4, 0, -tick),
            (w - inset - cs - 4, h - inset, -tick, 0),
        ]:
            p.drawLine(x, y, x + dx, y + dy)

        p.end()


# ── Timer bar ─────────────────────────────────────────────────────────────────
class TimerBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(6)
        self._fraction = 1.0

    def set_fraction(self, f: float):
        self._fraction = max(0.0, min(1.0, f))
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        w, h = self.width(), self.height()
        # Track
        p.fillRect(0, 0, w, h, QColor(CYAN_DIM))
        # Fill
        fill_w = int(w * self._fraction)
        if fill_w > 0:
            grad = QLinearGradient(0, 0, fill_w, 0)
            grad.setColorAt(0, QColor(CYAN_MID))
            grad.setColorAt(1, QColor(CYAN_GLOW))
            p.fillRect(0, 0, fill_w, h, grad)
        p.end()


# ── Main HUD Popup ─────────────────────────────────────────────────────────────
class HUDPopup(QWidget):
    def __init__(self):
        super().__init__()
        self._elapsed_ms = 0
        self._build_window()
        self._build_ui()
        self._timer = QTimer(self)
        self._timer.setInterval(TICK_MS)
        self._timer.timeout.connect(self._tick)

    # ── Window setup ──────────────────────────────────────────────────────────
    def _build_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(480)

    # ── Stylesheet helper ─────────────────────────────────────────────────────
    @staticmethod
    def _style():
        return f"""
        QWidget {{
            background: transparent;
            color: {TEXT_MID};
            font-family: 'Consolas', 'Courier New', monospace;
        }}
        QLabel#header_label {{
            color: {CYAN_GLOW};
            font-size: 10px;
            letter-spacing: 3px;
        }}
        QLabel#title_label {{
            color: {CYAN_BRIGHT};
            font-size: 13px;
            font-weight: bold;
            letter-spacing: 4px;
        }}
        QLabel#summary_label {{
            color: {TEXT_MID};
            font-size: 10px;
            letter-spacing: 1px;
        }}
        QLabel.field_label {{
            color: {TEXT_DIM};
            font-size: 9px;
            letter-spacing: 2px;
        }}
        QLabel.field_value {{
            color: {GREEN_DATA};
            font-size: 11px;
            font-weight: bold;
        }}
        QLabel#countdown_label {{
            color: {AMBER};
            font-size: 9px;
            letter-spacing: 2px;
        }}
        QPushButton#ok_btn {{
            background: transparent;
            border: 1px solid {CYAN_MID};
            color: {CYAN_BRIGHT};
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 10px;
            letter-spacing: 3px;
            padding: 4px 18px;
        }}
        QPushButton#ok_btn:hover {{
            background: {CYAN_DIM};
            border-color: {CYAN_GLOW};
            color: {CYAN_GLOW};
        }}
        QPushButton#ok_btn:pressed {{
            background: {CYAN_MID};
        }}
        """

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.setStyleSheet(self._style())

        # Root layout has a margin so the CornerFrame border is visible
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        # The actual painted container
        self._frame = CornerFrame(self)
        self._frame.setStyleSheet(f"background: {BG_DEEP};")
        root.addWidget(self._frame)

        inner = QVBoxLayout(self._frame)
        inner.setContentsMargins(16, 14, 16, 12)
        inner.setSpacing(8)

        # ── Top bar ──────────────────────────────────────────────────────────
        top_bar = QHBoxLayout()
        self._header_lbl = QLabel(f"// SYSTEM ALERT // {_rand_hex()}.{_rand_hex(4)}")
        self._header_lbl.setObjectName("header_label")
        top_bar.addWidget(self._header_lbl)
        top_bar.addStretch()
        id_lbl = QLabel(f"ID#{_rand_id()}")
        id_lbl.setObjectName("header_label")
        top_bar.addWidget(id_lbl)
        inner.addLayout(top_bar)

        # Separator
        inner.addWidget(self._make_sep())

        # ── Title ─────────────────────────────────────────────────────────────
        self._title_lbl = QLabel("SCANNING...")
        self._title_lbl.setObjectName("title_label")
        inner.addWidget(self._title_lbl)

        # ── Data rows container ───────────────────────────────────────────────
        self._data_widget = QWidget()
        self._data_layout = QVBoxLayout(self._data_widget)
        self._data_layout.setContentsMargins(4, 0, 4, 0)
        self._data_layout.setSpacing(4)
        inner.addWidget(self._data_widget)

        # ── Summary ───────────────────────────────────────────────────────────
        self._summary_lbl = QLabel("")
        self._summary_lbl.setObjectName("summary_label")
        self._summary_lbl.setWordWrap(True)
        inner.addWidget(self._summary_lbl)

        # Separator
        inner.addWidget(self._make_sep())

        # ── Timer bar + footer ────────────────────────────────────────────────
        self._timer_bar = TimerBar()
        inner.addWidget(self._timer_bar)

        footer = QHBoxLayout()
        self._countdown_lbl = QLabel("AUTO-CLOSE // 10s")
        self._countdown_lbl.setObjectName("countdown_label")
        footer.addWidget(self._countdown_lbl)
        footer.addStretch()
        ok_btn = QPushButton("[ CONFIRM ]")
        ok_btn.setObjectName("ok_btn")
        ok_btn.setFixedWidth(110)
        ok_btn.clicked.connect(self.close_popup)
        footer.addWidget(ok_btn)
        inner.addLayout(footer)

    def _make_sep(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background: {CYAN_DIM}; max-height: 1px;")
        return line

    # ── Public API ────────────────────────────────────────────────────────────
    def show_info(self, data: dict):
        """Populate the popup with AI-extracted data and show it."""
        self._elapsed_ms = 0
        self._title_lbl.setText(data.get("title", "DATA CAPTURED"))
        self._summary_lbl.setText(data.get("summary", ""))

        # Clear old rows
        while self._data_layout.count():
            item = self._data_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for entry in data.get("items", []):
            row = QHBoxLayout()
            lbl = QLabel(f"[{entry.get('label','?')}]")
            lbl.setProperty("class", "field_label")
            lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 9px; letter-spacing: 2px; font-family: Consolas, 'Courier New', monospace;")
            lbl.setFixedWidth(100)
            val = QLabel(entry.get("value", ""))
            val.setStyleSheet(f"color: {GREEN_DATA}; font-size: 11px; font-weight: bold; font-family: Consolas, 'Courier New', monospace;")
            val.setWordWrap(True)
            row.addWidget(lbl)
            row.addWidget(val)
            self._data_layout.addLayout(row)

        self.adjustSize()
        self._position_popup()
        self.show()
        self.raise_()
        self._timer.start()

    def close_popup(self):
        self._timer.stop()
        self.hide()

    # ── Timer tick ────────────────────────────────────────────────────────────
    def _tick(self):
        self._elapsed_ms += TICK_MS
        remaining_ms = AUTO_CLOSE_MS - self._elapsed_ms
        fraction = remaining_ms / AUTO_CLOSE_MS
        self._timer_bar.set_fraction(fraction)
        secs = max(0, int(remaining_ms / 1000) + 1)
        self._countdown_lbl.setText(f"AUTO-CLOSE // {secs:02d}s")
        if remaining_ms <= 0:
            self.close_popup()

    # ── Positioning ───────────────────────────────────────────────────────────
    def _position_popup(self):
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().availableGeometry()
        x = screen.right() - self.width() - 24
        y = screen.bottom() - self.height() - 48
        self.move(x, y)
