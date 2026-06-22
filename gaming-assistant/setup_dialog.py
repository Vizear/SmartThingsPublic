"""First-run setup dialog for entering the Anthropic API key."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QWidget,
)
from PyQt6.QtCore import Qt

BG     = "#050a14"
CYAN   = "#00d4e8"
CYAN_G = "#00e5ff"
CYAN_D = "#005f70"
GREEN  = "#39ff80"
TEXT   = "#7fcfdf"


class SetupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ALTANTIS HUD — SETUP")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setFixedWidth(440)
        self.api_key = ""
        self._build()

    def _build(self):
        self.setStyleSheet(f"""
            QDialog {{ background: {BG}; }}
            QLabel  {{ color: {TEXT}; font-family: Consolas, 'Courier New', monospace; font-size: 11px; }}
            QLabel#title {{ color: {CYAN_G}; font-size: 14px; font-weight: bold; letter-spacing: 4px; }}
            QLabel#sub   {{ color: {CYAN}; font-size: 9px; letter-spacing: 2px; }}
            QLineEdit {{
                background: #0a1628;
                border: 1px solid {CYAN_D};
                color: {GREEN};
                font-family: Consolas, 'Courier New', monospace;
                font-size: 12px;
                padding: 6px 10px;
            }}
            QLineEdit:focus {{ border-color: {CYAN}; }}
            QPushButton {{
                background: transparent;
                border: 1px solid {CYAN};
                color: {CYAN_G};
                font-family: Consolas, 'Courier New', monospace;
                font-size: 10px;
                letter-spacing: 3px;
                padding: 6px 20px;
            }}
            QPushButton:hover {{ background: {CYAN_D}; }}
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        title = QLabel("// ALTANTIS HUD SYSTEM //")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(title)

        sub = QLabel("GAMING ASSISTANT — INITIAL CONFIGURATION")
        sub.setObjectName("sub")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(sub)

        info = QLabel(
            "This application uses the Claude AI vision API to analyse your\n"
            "screen and surface important information while you play.\n\n"
            "Enter your Anthropic API key below to proceed.\n"
            "Your key is stored locally and never transmitted elsewhere."
        )
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setWordWrap(True)
        lay.addWidget(info)

        self._key_input = QLineEdit()
        self._key_input.setPlaceholderText("sk-ant-api03-...")
        self._key_input.setEchoMode(QLineEdit.EchoMode.Password)
        lay.addWidget(self._key_input)

        self._err = QLabel("")
        self._err.setStyleSheet(f"color: #ff4444; font-size: 9px; font-family: Consolas;")
        self._err.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self._err)

        btns = QHBoxLayout()
        cancel = QPushButton("[ CANCEL ]")
        cancel.clicked.connect(self.reject)
        btns.addWidget(cancel)
        confirm = QPushButton("[ CONFIRM ]")
        confirm.clicked.connect(self._confirm)
        btns.addWidget(confirm)
        lay.addLayout(btns)

    def _confirm(self):
        key = self._key_input.text().strip()
        if not key.startswith("sk-"):
            self._err.setText("ERROR: Key must start with  sk-")
            return
        self.api_key = key
        self.accept()
