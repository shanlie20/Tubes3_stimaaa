from functools import partial
from PySide6.QtWidgets import QApplication, QProgressBar, QMessageBox # Import QMessageBox
from PySide6.QtGui import QPalette
from PySide6.QtCore import Signal, Qt, QPropertyAnimation, QRect, QEasingCurve, QThread, QObject # Import QThread, QObject
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QButtonGroup,
    QPushButton,
    QSpinBox,
    QScrollArea,
    QFrame,
    QGridLayout,
    QSizePolicy
)

from src.core.search import perform_search
from .components.keyword_input import KeywordInput
from .components.result_card import ResultCard

class SearchWorker(QObject):
    finished = Signal(list, int, dict)
    error = Signal(str)

    def __init__(self, keywords_tuple, selected_algorithm, top_n):
        super().__init__()
        self.keywords_tuple = keywords_tuple
        self.selected_algorithm = selected_algorithm
        self.top_n = top_n

    def run(self):
        try:
            results, total_cv_scan, timings = perform_search(
                self.keywords_tuple,
                self.selected_algorithm,
                self.top_n
            )
            self.finished.emit(results, total_cv_scan, timings)
        except Exception as e:
            self.error.emit(f"An error occurred during search: {str(e)}")

class AlgorithmToggle(QWidget):
    """
    A custom toggle widget for selecting algorithms with a sliding animation.
    """
    algorithm_selected = Signal(str)

    def __init__(self, algorithms: list[str], parent=None):
        super().__init__(parent)
        self.algorithms = algorithms
        self.current_index = -1

        self.setFixedHeight(40)
        self.setMinimumWidth(len(algorithms) * 120 + 40)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(4, 2, 4, 2)
        self.main_layout.setSpacing(0)

        self.slider = QLabel(self)
        self.slider.setObjectName("slider")
        self.slider.setStyleSheet("""
            QLabel#slider {
                background-color: #4CAF50;
                border-radius: 8px;
            }
        """)
        self.slider.setGeometry(0, 0, 0, 0)

        self.current_animation = QPropertyAnimation(self.slider, b"geometry", self)
        self.current_animation.setDuration(200)
        self.current_animation.setEasingCurve(QEasingCurve.OutCubic)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.buttons = []

        for i, algo_name in enumerate(self.algorithms):
            btn = QPushButton(algo_name, self)
            btn.setCheckable(True)
            btn.setObjectName("algoToggleButton")
            btn.setStyleSheet("""
                QPushButton#algoToggleButton {
                    background-color: transparent;
                    border: none;
                    color: #555;
                    font-size: 10pt;
                    font-weight: normal;
                    padding: 8px 16px;
                }
                QPushButton#algoToggleButton:hover {
                    background-color: rgba(0, 0, 0, 0.05);
                    border: 1px solid #c0c0c0;
                    border-radius: 8px;
                }
                QPushButton#algoToggleButton:checked {
                    color: white;
                    font-weight: bold;
                }
            """)
            btn.setMinimumWidth(120)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

            self.main_layout.addWidget(btn)
            self.button_group.addButton(btn, i)
            self.buttons.append(btn)

            btn.toggled.connect(partial(self._on_button_toggled, btn, i))

        self.setStyleSheet("""
            AlgorithmToggle {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #ccc;
            }
        """)

    def showEvent(self, event):
        super().showEvent(event)
        if not self.button_group.checkedButton():
            self.slider.setVisible(False)
        else:
            self.slider.setVisible(True)
            checked_button = self.button_group.checkedButton()
            index = self.button_group.id(checked_button)
            self._position_slider(checked_button, index, animate=False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.buttons and self.button_group.checkedButton():
            checked_button = self.button_group.checkedButton()
            index = self.button_group.id(checked_button)
            self._position_slider(checked_button, index, animate=False)

    def _on_button_toggled(self, button: QPushButton, index: int, checked: bool):
        if checked:
            self.current_index = index
            self.slider.setVisible(True)
            self._position_slider(button, index)
            self.algorithm_selected.emit(button.text())
        else:
            pass

    def _position_slider(self, target_button: QPushButton, index: int, animate=True):
        if self.current_animation.state() == QPropertyAnimation.Running:
            self.current_animation.stop()

        final_rect = target_button.geometry()

        if animate:
            self.current_animation.setStartValue(self.slider.geometry())
            self.current_animation.setEndValue(final_rect)
            self.current_animation.start()
        else:
            self.slider.setGeometry(final_rect)


class SearchPage(QWidget):
    """Page that lets the recruiter search CVs by keyword."""

    summary_requested = Signal(int, str, str)
    view_cv_requested = Signal(str, str)

    def __init__(self) -> None:
        super().__init__()
        app_palette = QApplication.instance().palette()
        window_color = app_palette.color(QPalette.ColorRole.Window)
        theme_name = "dark" if window_color.lightness() < 128 else "light"
        self.setProperty("theme", theme_name)
        self.current_page = 0
        self.results_per_page = 10
        self.all_results = []
        self._build_ui()
        self._show_initial_message()
        self.showMaximized()

        self.search_thread = None
        self.search_worker = None

    # UI construction
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        # Title
        title = QLabel("Applicant Tracking System - CV Search")
        title.setObjectName("h1")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        root.addWidget(title)

        # Keyword input
        self.keyword_input = KeywordInput(placeholder="Enter keywords, separated by commas...")
        root.addWidget(self.keyword_input)

        # Algorithm selector (Animated Toggle) & Top-N selector
        algorithm_selection_layout = QHBoxLayout()
        algorithm_selection_layout.setContentsMargins(0, 2, 0, 2)

        algorithm_label = QLabel("Select Algorithm:")
        algorithm_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        algorithm_label.setStyleSheet("font-weight: bold; font-size: 10pt;")
        algorithm_selection_layout.addWidget(algorithm_label)

        self.algo_toggle = AlgorithmToggle(algorithms=["KMP", "Boyer-Moore", "Aho-Corasick"])
        self.algo_toggle.algorithm_selected.connect(self._on_algorithm_selected)
        self.algo_toggle.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        algorithm_selection_layout.addWidget(self.algo_toggle)

        # Top-N spinbox
        algorithm_selection_layout.addStretch(1)
        top_label = QLabel("Top matches:")
        self.top_spin = QSpinBox()
        self.top_spin.setRange(1, 600)
        self.top_spin.setValue(8)
        algorithm_selection_layout.addWidget(top_label)
        algorithm_selection_layout.addWidget(self.top_spin)

        root.addLayout(algorithm_selection_layout)

        # Search button
        self.search_btn = QPushButton("Search")
        self.search_btn.setDefault(True)
        self.search_btn.clicked.connect(self._on_search_clicked)
        root.addWidget(self.search_btn)


        # Summary execution time and total CVs
        info_layout = QHBoxLayout()
        self.exec_time_lbl = QLabel("")
        self.total_cv_lbl = QLabel("")
        info_layout.addWidget(self.exec_time_lbl)
        info_layout.addStretch(1)
        info_layout.addWidget(self.total_cv_lbl)
        root.addLayout(info_layout)

        # White background frame for results
        self.results_background_frame = QFrame()
        self.results_background_frame.setObjectName("resultsBackgroundFrame")
        self.results_background_frame.setStyleSheet("""
            QFrame#resultsBackgroundFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
        """)
        self.results_frame_layout = QVBoxLayout(self.results_background_frame)
        self.results_frame_layout.setContentsMargins(15, 15, 15, 15)
        self.results_frame_layout.setSpacing(10)

        # Results area (Scrollable)
        self.results_scroll_area = QScrollArea()
        self.results_scroll_area.setWidgetResizable(True)
        self.results_container = QWidget()
        self.results_container.setStyleSheet("QWidget { background-color: white; }")
        self.results_grid_layout = QGridLayout(self.results_container)
        self.results_grid_layout.setSpacing(10)
        self.results_scroll_area.setWidget(self.results_container)
        
        self.results_frame_layout.addWidget(self.results_scroll_area)

        # Loading Spinner (QProgressBar in indeterminate mode) and Text
        self.loading_spinner = QProgressBar()
        self.loading_spinner.setRange(0, 0)
        self.loading_spinner.setTextVisible(False)
        self.loading_spinner.setFixedSize(50, 50)
        self.loading_spinner.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: transparent;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 25px;
            }
        """)
        
        self.loading_text_label = QLabel("Loading . . .")
        self.loading_text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_text_label.setStyleSheet("font-size: 14pt; color: #555;")


        spinner_center_layout = QHBoxLayout()
        spinner_center_layout.addStretch(1)
        spinner_center_layout.addWidget(self.loading_spinner)
        spinner_center_layout.addStretch(1)
        
        self.loading_v_layout = QVBoxLayout()
        self.loading_v_layout.addStretch(1)
        self.loading_v_layout.addLayout(spinner_center_layout)
        self.loading_v_layout.addWidget(self.loading_text_label)
        self.loading_v_layout.addSpacing(20)
        self.loading_v_layout.addStretch(1)

        self.loading_widget = QWidget()
        self.loading_widget.setLayout(self.loading_v_layout)
        self.loading_widget.hide()

        self.results_frame_layout.addWidget(self.loading_widget)
        
        self.results_frame_layout.setStretchFactor(self.results_scroll_area, 1)
        self.results_frame_layout.setStretchFactor(self.loading_widget, 1)

        root.addWidget(self.results_background_frame, 1)

        # Pagination Controls
        self.pagination_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self._prev_page)
        self.prev_button.setEnabled(False)
        self.page_info_label = QLabel("Page 0 of 0")
        self.page_info_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self._next_page)
        self.next_button.setEnabled(False)

        self.pagination_layout.addStretch(1)
        self.pagination_layout.addWidget(self.prev_button)
        self.pagination_layout.addWidget(self.page_info_label)
        self.pagination_layout.addWidget(self.next_button)
        self.pagination_layout.addStretch(1)
        root.addLayout(self.pagination_layout)

        # Styling for the main page
        self.setStyleSheet(
            """
            QLabel#h1 {
                font-size: 20pt;
                font-weight: bold;
            }
            SearchPage[theme="light"] QLabel#h1 {
                color: #333;
            }
            SearchPage[theme="dark"] QLabel#h1 {
                color: white;
            }
            """
        )
        self.selected_algorithm = None

    def _show_initial_message(self):
        """Displays a message in the results area when no search has been performed."""
        self.loading_widget.hide()
        self.results_scroll_area.show()
        self._clear_grid_layout()

        message_label = QLabel("Please input keywords, top matches, and select an algorithm to perform a search.")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("color: #888; font-style: italic; font-size: 16px;")
        message_label.setWordWrap(True)

        self.results_grid_layout.addWidget(message_label, 0, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.results_grid_layout.setRowStretch(0, 1)
        self.results_grid_layout.setColumnStretch(0, 1)

    def _clear_grid_layout(self):
        """Helper method to completely clear the grid layout"""
        while self.results_grid_layout.count():
            item = self.results_grid_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.spacerItem():
                self.results_grid_layout.removeItem(item)

        for i in range(self.results_grid_layout.rowCount()):
            self.results_grid_layout.setRowStretch(i, 0)
        for i in range(self.results_grid_layout.columnCount()):
            self.results_grid_layout.setColumnStretch(i, 0)

    # Event handlers
    def _on_algorithm_selected(self, algorithm_name: str):
        """Receives the selected algorithm from the AlgorithmToggle widget."""
        self.selected_algorithm = algorithm_name

    def _on_search_clicked(self):
        keywords = self.keyword_input.keywords()
        if not keywords:
            self.exec_time_lbl.setText("Please enter at least one keyword!")
            self.total_cv_lbl.setText("")
            self._show_initial_message()
            return

        if self.selected_algorithm is None:
            self.exec_time_lbl.setText("Please select an algorithm!")
            self.total_cv_lbl.setText("")
            return

        self._set_ui_enabled(False)

        self._clear_grid_layout()
        self.results_scroll_area.hide()
        self.loading_widget.show()

        top_n = self.top_spin.value()
        keywords_tuple = tuple(keywords)

        self.search_thread = QThread()
        self.search_worker = SearchWorker(keywords_tuple, self.selected_algorithm, top_n)
        
        self.search_worker.moveToThread(self.search_thread)

        self.search_thread.started.connect(self.search_worker.run)
        self.search_worker.finished.connect(self._on_search_finished)
        self.search_worker.error.connect(self._on_search_error)
        
        self.search_worker.finished.connect(self.search_thread.quit)
        self.search_worker.finished.connect(self.search_worker.deleteLater)
        self.search_thread.finished.connect(self.search_thread.deleteLater)
        
        self.search_thread.start()

    def _on_search_finished(self, results, total_cv_scan, timings):
        self.all_results = results
        self.current_page = 0

        self.exec_time_lbl.setText(
            f"Exact Search Time ({self.selected_algorithm}): {timings['exact_ms']:.2f} ms"
            f" | Fuzzy Match: {timings['fuzzy_ms']:.2f} ms"
        )
        self.total_cv_lbl.setText(f"Total CVs Processed: {total_cv_scan}")

        self.loading_widget.hide()
        self.results_scroll_area.show()
        self._populate_current_page_results()
        self._update_pagination_buttons()

        self._set_ui_enabled(True)

    def _on_search_error(self, message):
        QMessageBox.critical(self, "Search Error", message)
        
        self.loading_widget.hide()
        self.results_scroll_area.show()
        self._show_initial_message()

        self._set_ui_enabled(True)

    def _set_ui_enabled(self, enabled: bool):
        """Helper to enable/disable main UI elements during search."""
        self.keyword_input.setEnabled(enabled)
        self.algo_toggle.setEnabled(enabled)
        self.top_spin.setEnabled(enabled)
        self.search_btn.setEnabled(enabled)
        
        self.prev_button.setEnabled(enabled and self.current_page > 0)
        total_pages = (len(self.all_results) + self.results_per_page - 1) // self.results_per_page
        self.next_button.setEnabled(enabled and self.current_page < total_pages - 1)


    def _populate_current_page_results(self):
        self._clear_grid_layout()

        start_index = self.current_page * self.results_per_page
        end_index = start_index + self.results_per_page
        current_page_results = self.all_results[start_index:end_index]

        num_cols = 4
        min_rows_to_display = 2

        if not current_page_results and max(len(self.all_results), min_rows_to_display * num_cols) == 0:
            no_results_label = QLabel("No results found for the given keywords. Try different keywords.")
            no_results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_results_label.setStyleSheet("color: #888; font-style: italic; font-size: 16px;")
            no_results_label.setWordWrap(True)

            self.results_grid_layout.addWidget(no_results_label, 0, 0, 1, num_cols, Qt.AlignmentFlag.AlignCenter)
            self.results_grid_layout.setRowStretch(0, 1)
            self.results_grid_layout.setColumnStretch(0, 1)
            return
        elif not current_page_results:
            no_results_label = QLabel("No results found for the given keywords. Try different keywords.")
            no_results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_results_label.setStyleSheet("color: #888; font-style: italic; font-size: 16px;")
            no_results_label.setWordWrap(True)
            self.results_grid_layout.addWidget(no_results_label, 0, 0, min_rows_to_display, num_cols, Qt.AlignmentFlag.AlignCenter)

            for i in range(num_cols):
                self.results_grid_layout.setColumnStretch(i, 1)
            for i in range(min_rows_to_display):
                self.results_grid_layout.setRowStretch(i, 1)
            return

        row, col = 0, 0
        for i in range(max(len(current_page_results), min_rows_to_display * num_cols)):
            if i < len(current_page_results):
                res = current_page_results[i]
                card = ResultCard(res)
                card.summary_clicked.connect(self.summary_requested.emit)
                card.view_cv_clicked.connect(partial(self.view_cv_requested.emit, res.get("name", "N/A"), res.get("cv_content", "CV content not available.")))
                self.results_grid_layout.addWidget(card, row, col)
            else:
                placeholder_widget = QWidget()
                placeholder_widget.setMinimumSize(150, 100)
                placeholder_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                self.results_grid_layout.addWidget(placeholder_widget, row, col)

            col += 1
            if col >= num_cols:
                col = 0
                row += 1

        for i in range(num_cols):
            self.results_grid_layout.setColumnStretch(i, 1)
        
        for i in range(max(row, min_rows_to_display)):
            self.results_grid_layout.setRowStretch(i, 1)

    def _update_pagination_buttons(self):
        total_pages = (len(self.all_results) + self.results_per_page - 1) // self.results_per_page
        display_total_pages = max(1, total_pages)
        self.page_info_label.setText(f"Page {self.current_page + 1} of {display_total_pages}")

        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < total_pages - 1)

    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._populate_current_page_results()
            self._update_pagination_buttons()

    def _next_page(self):
        total_pages = (len(self.all_results) + self.results_per_page - 1) // self.results_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self._populate_current_page_results()
            self._update_pagination_buttons()