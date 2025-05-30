from PySide6.QtWidgets import QMainWindow, QWidget, QStackedLayout
from PySide6.QtCore import Qt

from ui.search_page import SearchPage
from ui.summary_page import SummaryPage


class MainWindow(QMainWindow):
    """Main application window with a stacked layout for page navigation."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ATS - CV Search & Summary")
        self.resize(1000, 700)

        # Central container with stacked pages
        container = QWidget()
        self.setCentralWidget(container)
        self._stack = QStackedLayout(container)

        # Pages
        self.search_page = SearchPage()
        self.summary_page = SummaryPage()

        self._stack.addWidget(self.search_page)
        self._stack.addWidget(self.summary_page)

        # --- wire signals ---
        self.search_page.summary_requested.connect(self._show_summary_page)
        self.summary_page.back_requested.connect(self._show_search_page)

    # ------------------------------------------------------------------
    # Navigation helpers
    # ------------------------------------------------------------------
    def _show_summary_page(self, candidate_data: dict):
        """Navigate to the summary page and load data for the selected candidate."""
        self.summary_page.load_candidate(candidate_data)
        self._stack.setCurrentWidget(self.summary_page)

    def _show_search_page(self):
        """Navigate back to the search page."""
        self._stack.setCurrentWidget(self.search_page)
