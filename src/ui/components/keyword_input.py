from PySide6.QtWidgets import QWidget, QLineEdit, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class KeywordInput(QWidget):
    """Simple widget wrapping QLineEdit for entering comma-separated keywords."""

    def __init__(self, placeholder: str = "") -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText(placeholder)
        layout.addWidget(self.line_edit)

        hint = QLabel("Separate keywords with commas, e.g.: Python, React, SQL")
        hint.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        hint.setStyleSheet("color: gray; font-size: 10pt;")
        layout.addWidget(hint)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def keywords(self) -> list[str]:
        """Return a list of trimmed, non-empty keywords entered by the user."""
        text = self.line_edit.text()
        return [kw.strip() for kw in text.split(",") if kw.strip()]
