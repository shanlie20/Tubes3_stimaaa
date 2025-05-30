from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
)


class SummaryPage(QWidget):
    """Displays extracted summary information for a single candidate CV."""

    back_requested = Signal()

    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        # Back button
        back_btn = QPushButton("←  Back to Search")
        back_btn.clicked.connect(self.back_requested.emit)
        root.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        # Candidate name
        self.name_lbl = QLabel("Candidate Name")
        self.name_lbl.setObjectName("h2")
        root.addWidget(self.name_lbl)

        # Summary text
        self.summary_txt = QTextEdit(readOnly=True)
        root.addWidget(self.summary_txt, 1)

        # View CV button placeholder (could open PDF)
        self.view_cv_btn = QPushButton("Open CV PDF …")
        self.view_cv_btn.setEnabled(False)
        root.addWidget(self.view_cv_btn, alignment=Qt.AlignmentFlag.AlignRight)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def load_candidate(self, data: dict):
        """Load candidate details into the UI."""
        self.name_lbl.setText(data.get("name", "<Unknown>"))
        # Placeholder summary – replace when regex extraction is ready
        self.summary_txt.setPlainText(
            f"Matched keywords (total {data.get('match_count', 0)}):\n"
            + ", ".join(data.get("matched_keywords", []))
        )
        # TODO: connect view_cv_btn to open PDF via utils/file_utils.py
        self.view_cv_btn.setEnabled(False)
