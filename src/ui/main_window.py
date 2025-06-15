
from PySide6.QtWidgets import QMainWindow, QWidget, QStackedLayout
from PySide6.QtCore import Qt

from .search_page import SearchPage
from .summary_page import SummaryPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ATS - CV Search & Summary by stimaaa")
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

        # Wire signals
        self.search_page.summary_requested.connect(self._show_summary_page)
        self.summary_page.back_requested.connect(self._show_search_page)

    def _show_summary_page(self, applicant_id: int, cv_path: str, cv_content: str):
        """Navigate to the summary page and load data for the selected candidate."""
        self.summary_page.load_candidate(applicant_id, cv_path, cv_content)
        self._stack.setCurrentWidget(self.summary_page)

    def _show_search_page(self):
        """Navigate back to the search page."""
        self._stack.setCurrentWidget(self.search_page)
