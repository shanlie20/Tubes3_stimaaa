from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton
)
from PySide6.QtGui import QDesktopServices

class ResultCard(QFrame):
    """Card widget showing basic information about a CV match."""

    # MODIFIED: Change signal to emit only int (applicant_id)
    summary_clicked = Signal(int) # Emits the applicant_id for summary
    view_cv_clicked = Signal(str) # Emits the cv_path string for viewing CV

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

        # Top section: Name (left) and Total Matches (right)
        top_h_layout = QHBoxLayout()
        name_lbl = QLabel(self._data.get("name", "<Unknown>"))
        name_lbl.setObjectName("h3")
        top_h_layout.addWidget(name_lbl)
        top_h_layout.addStretch(1) # Pushes match_count_lbl to the right

        total_matches_lbl = QLabel(f"{self._data.get('total_matches', 0)} matches")
        top_h_layout.addWidget(total_matches_lbl)
        main_v_layout.addLayout(top_h_layout)

        # Matched keywords section
        matched_keywords_title_lbl = QLabel("Matched keywords:")
        main_v_layout.addWidget(matched_keywords_title_lbl)

        # Keyword list with numbering and occurrences
        keywords_list_layout = QVBoxLayout()
        matched_keywords_detail = self._data.get("matched_keywords_detail", {})

        # Sort keywords for consistent numbering, though not strictly required by request
        sorted_keywords = sorted(matched_keywords_detail.items(), key=lambda item: item[0])

        for i, (keyword, occurrence) in enumerate(sorted_keywords):
            keyword_lbl = QLabel(f"{i+1}. {keyword}: {occurrence} occurence{'s' if occurrence > 1 else ''}")
            keywords_list_layout.addWidget(keyword_lbl)

        main_v_layout.addLayout(keywords_list_layout)

        main_v_layout.addStretch(1) # Pushes buttons to the bottom

        # Bottom section: Buttons (Summary left, View CV right)
        bottom_h_layout = QHBoxLayout()
        summary_btn = QPushButton("Summary")
        # MODIFIED: Emit only applicant_id
        summary_btn.clicked.connect(lambda: self.summary_clicked.emit(self._data.get("applicant_id")))
        bottom_h_layout.addWidget(summary_btn)

        bottom_h_layout.addStretch(1) # Pushes View CV button to the right

        view_cv_btn = QPushButton("View CV")
        # Pass cv_path for viewing the CV
        view_cv_btn.clicked.connect(self.open_cv_pdf)
        bottom_h_layout.addWidget(view_cv_btn)
        main_v_layout.addLayout(bottom_h_layout)

        # Style hint – could be moved to a global stylesheet
        self.setStyleSheet(
            """
            QFrame#resultCard {
                border: 1px solid #ccc;
                border-radius: 8px;
            }
            QFrame#resultCard QLabel, QFrame#resultCard QPushButton {
                color: black;
            }
            QLabel#h3 {
                font-size: 14pt;
                font-weight: bold;
            }
            QFrame#resultCard QPushButton {
                color: black;
                background-color: white;
                border: 1px solid black;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QFrame#resultCard QPushButton:hover {
                background-color: #f0f0f0;  /* Latar belakang abu-abu saat kursor di atas */
            }
            """
        )

    def open_cv_pdf(self):
        """Open the CV PDF based on the cv_path."""
        cv_path = self._data.get("cv_path", "")  # Mendapatkan cv_path dari data kandidat

        if cv_path:
            # Convert the file path to a URL
            cv_url = QUrl.fromLocalFile(cv_path)
            # Use QDesktopServices to open the URL in the default PDF viewer
            QDesktopServices.openUrl(cv_url)
        else:
            print("CV file not found!")