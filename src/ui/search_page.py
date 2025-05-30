from functools import partial

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QButtonGroup,
    QRadioButton,
    QSpinBox,
    QPushButton,
    QScrollArea,
    QFrame,
)

from ui.components.keyword_input import KeywordInput
from ui.components.result_card import ResultCard

# Stub to core search logic – replace with real implementation later
try:
    from core.search import perform_search  # type: ignore
except ModuleNotFoundError:
    def perform_search(keywords, algorithm, top_n):  # type: ignore
        """Placeholder search implementation returning dummy data."""
        dummy = [
            {
                "name": f"Candidate {i + 1}",
                "match_count": len(keywords) - i % len(keywords),
                "matched_keywords": keywords,
                "candidate_id": i + 1,
            }
            for i in range(top_n)
        ]
        timings = {
            "exact_ms": 120,
            "fuzzy_ms": 150,
        }
        return dummy, timings


class SearchPage(QWidget):
    """Page that lets the recruiter search CVs by keyword."""

    summary_requested = Signal(dict)

    def __init__(self) -> None:
        super().__init__()
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        # -- Title --
        title = QLabel("Applicant Tracking System – CV Search")
        title.setObjectName("h1")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        root.addWidget(title)

        # -- Keyword input --
        self.keyword_input = KeywordInput(placeholder="Masukkan keyword, pisahkan dengan koma …")
        root.addWidget(self.keyword_input)

        # -- Algorithm selector & top‑N selector --
        line = QHBoxLayout()

        # Radio buttons for algorithm
        self.alg_group = QButtonGroup(self)
        rb_kmp = QRadioButton("KMP")
        rb_bm = QRadioButton("Boyer-Moore")
        rb_ac = QRadioButton("Aho-Corasick")
        rb_kmp.setChecked(True)
        self.alg_group.addButton(rb_kmp)
        self.alg_group.addButton(rb_bm)
        self.alg_group.addButton(rb_ac)

        line.addWidget(rb_kmp)
        line.addWidget(rb_bm)
        line.addWidget(rb_ac)

        # Top‑N spinbox
        line.addStretch(1)
        top_label = QLabel("Top matches:")
        self.top_spin = QSpinBox()
        self.top_spin.setRange(1, 100)
        self.top_spin.setValue(10)
        line.addWidget(top_label)
        line.addWidget(self.top_spin)

        root.addLayout(line)

        # -- Search button --
        self.search_btn = QPushButton("Search")
        self.search_btn.setDefault(True)
        self.search_btn.clicked.connect(self._on_search_clicked)
        root.addWidget(self.search_btn)

        # -- Summary execution time --
        self.exec_time_lbl = QLabel("")
        root.addWidget(self.exec_time_lbl)

        # -- Results area --
        self.results_area = QScrollArea()
        self.results_area.setWidgetResizable(True)
        results_container = QWidget()
        self.results_layout = QVBoxLayout(results_container)
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.results_area.setWidget(results_container)
        root.addWidget(self.results_area, 1)

        # Styling placeholder via object names – use Qt stylesheets in main if needed

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def _on_search_clicked(self):
        keywords = self.keyword_input.keywords()
        if not keywords:
            self.exec_time_lbl.setText("Masukkan minimal satu keyword!")
            return

        algorithm = "KMP" if self.alg_group.buttons()[0].isChecked() else "BM"
        top_n = self.top_spin.value()

        # search
        results, timings = perform_search(keywords, algorithm, top_n)

        # update timings label
        self.exec_time_lbl.setText(
            f"Exact Match: {timings['exact_ms']} ms | Fuzzy Match: {timings['fuzzy_ms']} ms"
        )

        # populate result cards
        self._populate_results(results)

    def _populate_results(self, results):
        # clear old cards
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for res in results:
            card = ResultCard(res)
            card.summary_clicked.connect(lambda checked=False, d=res: self.summary_requested.emit(d))
            self.results_layout.addWidget(card)

        self.results_layout.addStretch(1)
