from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
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
        # Main vertical layout for the card
        main_v_layout = QVBoxLayout(self)
        main_v_layout.setContentsMargins(16, 12, 16, 12)
        main_v_layout.setSpacing(10) # Adjust spacing as needed

        # Top section: Name and Total Matches
        top_h_layout = QHBoxLayout()
        name_lbl = QLabel(self._data.get("name", "<Unknown>"))
        name_lbl.setObjectName("h3")
        top_h_layout.addWidget(name_lbl)
        top_h_layout.addStretch(1) # Pushes match_count_lbl to the right

        match_count_lbl = QLabel(f"{self._data.get('match_count', 0)} matches")
        top_h_layout.addWidget(match_count_lbl)
        main_v_layout.addLayout(top_h_layout)

        # Matched keywords section
        # Original 'match_lbl' is now the title for "Matched keywords"
        matched_keywords_title_lbl = QLabel("Matched keywords:")
        main_v_layout.addWidget(matched_keywords_title_lbl)

        # Keyword list
        # Using a QVBoxLayout for the list of keywords and their occurrences
        keywords_list_layout = QVBoxLayout()
        for i, (keyword, occurrence) in enumerate(self._data.get("matched_keywords_detail", {}).items()):
            keyword_lbl = QLabel(f"{i+1}. {keyword}: {occurrence} occurence{'s' if occurrence > 1 else ''}")
            keywords_list_layout.addWidget(keyword_lbl)
        main_v_layout.addLayout(keywords_list_layout)


        main_v_layout.addStretch(1) # Pushes buttons to the bottom

        # Bottom section: Buttons
        bottom_h_layout = QHBoxLayout()
        summary_btn = QPushButton("Summary")
        summary_btn.clicked.connect(self.summary_clicked.emit)
        bottom_h_layout.addWidget(summary_btn)

        bottom_h_layout.addStretch(1) # Pushes View CV button to the right

        view_cv_btn = QPushButton("View CV")
        view_cv_btn.clicked.connect(self.view_cv_clicked.emit)
        bottom_h_layout.addWidget(view_cv_btn)
        main_v_layout.addLayout(bottom_h_layout)

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