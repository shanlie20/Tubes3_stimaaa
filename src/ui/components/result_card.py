from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
)


class ResultCard(QFrame):
    """Card widget showing basic information about a CV match."""

    summary_clicked = Signal()
    view_cv_clicked = Signal()

    def __init__(self, data: dict):
        super().__init__()
        self._data = data
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("resultCard")
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(24)

        # Left – basic info
        info_col = QVBoxLayout()
        name_lbl = QLabel(self._data.get("name", "<Unknown>"))
        name_lbl.setObjectName("h3")
        info_col.addWidget(name_lbl)

        match_lbl = QLabel(f"Jumlah kecocokan: {self._data.get('match_count', 0)}")
        info_col.addWidget(match_lbl)

        kw_lbl = QLabel(", ".join(self._data.get("matched_keywords", [])))
        kw_lbl.setWordWrap(True)
        info_col.addWidget(kw_lbl)

        info_col.addStretch(1)
        layout.addLayout(info_col, 3)

        # Right – action buttons
        btn_col = QVBoxLayout()
        summary_btn = QPushButton("Summary")
        summary_btn.clicked.connect(self.summary_clicked.emit)
        view_cv_btn = QPushButton("View CV")
        view_cv_btn.clicked.connect(self.view_cv_clicked.emit)
        btn_col.addWidget(summary_btn)
        btn_col.addWidget(view_cv_btn)
        btn_col.addStretch(1)
        layout.addLayout(btn_col, 1)

        # Style hint – could be moved to a global stylesheet
        self.setStyleSheet(
            """
            QFrame#resultCard {
                border: 1px solid #ccc;
                border-radius: 8px;
            }
            QLabel#h3 {
                font-size: 14pt;
                font-weight: bold;
            }
            """
        )
