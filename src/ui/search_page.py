from functools import partial
from PySide6.QtWidgets import QApplication 
from PySide6.QtGui import QPalette
from PySide6.QtCore import Signal, Qt, QPropertyAnimation, QRect, QEasingCurve
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
    QSpacerItem,
    QSizePolicy
)

# Assume these imports are correct and available
from src.core.search import perform_search
from .components.keyword_input import KeywordInput
from .components.result_card import ResultCard
from src.core.pdf_parser import parse_pdf_to_text
from src.utils.timer import start_timer, stop_timer
from src.utils.keyword_utils import normalize_text, tokenize_text, remove_stopwords, extract_unique_keywords
from src.utils.file_utils import read_file_content


class AlgorithmToggle(QWidget):
    """
    A custom toggle widget for selecting algorithms with a sliding animation.
    """
    algorithm_selected = Signal(str) # Emits the text of the selected algorithm
    
    def __init__(self, algorithms: list[str], parent=None):
        super().__init__(parent)
        self.algorithms = algorithms
        self.current_index = -1 # No default selected algorithm initially

        self.setFixedHeight(40) # Fixed height for the toggle widget
        # Set a minimum width for the toggle widget to ensure it can fit all buttons
        self.setMinimumWidth(len(algorithms) * 120 + 40) 
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed) # Allow horizontal expansion

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(4, 2, 4, 2) # Slightly increased horizontal padding for the track
        self.main_layout.setSpacing(0)

        # Background slider - This will now represent the active, green area *behind* the text
        self.slider = QLabel(self)
        self.slider.setObjectName("slider")
        self.slider.setStyleSheet("""
            QLabel#slider {
                background-color: #4CAF50; /* Green background for the slider */
                border-radius: 8px;
            }
        """)
        self.slider.setGeometry(0, 0, 0, 0) # Initial geometry will be set in _position_slider

        self.current_animation = QPropertyAnimation(self.slider, b"geometry", self)
        self.current_animation.setDuration(200) # milliseconds
        self.current_animation.setEasingCurve(QEasingCurve.OutCubic)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True) # Only one button can be checked at a time
        self.buttons = []

        for i, algo_name in enumerate(self.algorithms):
            btn = QPushButton(algo_name, self)
            btn.setCheckable(True)
            btn.setObjectName("algoToggleButton")
            btn.setStyleSheet("""
                QPushButton#algoToggleButton {
                    background-color: transparent; /* Initially transparent to show parent's background */
                    border: none;
                    color: #555; /* Dark gray text for unselected buttons */
                    font-size: 10pt;
                    font-weight: normal;
                    padding: 8px 16px; 
                }
                QPushButton#algoToggleButton:hover {
                    background-color: rgba(0, 0, 0, 0.05); /* Slight hover effect on the white background */
                    border: 1px solid #c0c0c0;
                    border-radius: 8px;
                }
                QPushButton#algoToggleButton:checked {
                    /* When checked, the slider will be behind it, so we ensure text color contrasts with green */
                    color: white; /* White text for selected button (on green slider) */
                    font-weight: bold;
                }
            """)
            btn.setMinimumWidth(120) 
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            
            self.main_layout.addWidget(btn)
            self.button_group.addButton(btn, i)
            self.buttons.append(btn)
            
            btn.toggled.connect(partial(self._on_button_toggled, btn, i))

        # Main container styling (the "track" background)
        self.setStyleSheet("""
            AlgorithmToggle {
                background-color: white; /* White background for the entire toggle track */
                border-radius: 10px;
                border: 1px solid #ccc; /* Add a subtle border */
            }
        """)

    def showEvent(self, event):
        super().showEvent(event)
        # On initial show, if no button is checked, ensure the slider is hidden or not positioned
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
            self.slider.setVisible(True) # Make slider visible when a button is selected
            self._position_slider(button, index) # Animate by default
            self.algorithm_selected.emit(button.text())
        else:
            # If a button is unchecked (due to another being selected), the slider will move
            # We don't need to hide it here, as it's always under one button.
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

    summary_requested = Signal(dict)
    view_cv_requested = Signal(str, str) # New signal for viewing CV (applicant name, cv content)

    def __init__(self) -> None:
        super().__init__()
        app_palette = QApplication.instance().palette()
        window_color = app_palette.color(QPalette.ColorRole.Window)
        theme_name = "dark" if window_color.lightness() < 128 else "light"
        self.setProperty("theme", theme_name)
        self.current_page = 0
        self.results_per_page = 10 # This implies 2 rows of 5 cards
        self.all_results = []
        self._build_ui()
        self._show_initial_message()
        self.showMaximized() # Add this line to maximize the window on startup

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        # -- Title --
        title = QLabel("Applicant Tracking System - CV Search")
        title.setObjectName("h1")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        root.addWidget(title)

        # -- Keyword input --
        self.keyword_input = KeywordInput(placeholder="Enter keywords, separated by commas...")
        root.addWidget(self.keyword_input)
        
        # -- Algorithm selector (Animated Toggle) & Top-N selector --
        algorithm_selection_layout = QHBoxLayout()
        # Adjusted contents margins to reduce top and bottom padding
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
        self.top_spin.setRange(1, 480) 
        self.top_spin.setValue(10)
        algorithm_selection_layout.addWidget(top_label)
        algorithm_selection_layout.addWidget(self.top_spin)

        root.addLayout(algorithm_selection_layout)

        # -- Search button --
        self.search_btn = QPushButton("Search")
        self.search_btn.setDefault(True)
        self.search_btn.clicked.connect(self._on_search_clicked)
        root.addWidget(self.search_btn)

        # -- Summary execution time and total CVs (moved here) --
        info_layout = QHBoxLayout()
        self.exec_time_lbl = QLabel("")
        self.total_cv_lbl = QLabel("")
        info_layout.addWidget(self.exec_time_lbl)
        info_layout.addStretch(1)
        info_layout.addWidget(self.total_cv_lbl)
        root.addLayout(info_layout) # Added directly to the root layout

        # --- White background frame for results ---
        self.results_background_frame = QFrame()
        self.results_background_frame.setObjectName("resultsBackgroundFrame")
        self.results_background_frame.setStyleSheet("""
            QFrame#resultsBackgroundFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
        """)
        results_frame_layout = QVBoxLayout(self.results_background_frame)
        results_frame_layout.setContentsMargins(15, 15, 15, 15) # Padding inside the white box
        results_frame_layout.setSpacing(10)

        # -- Results area (Scrollable) (moved into the new frame) --
        self.results_scroll_area = QScrollArea()
        self.results_scroll_area.setWidgetResizable(True)
        self.results_container = QWidget()
        # Set the background of the results_container to white
        self.results_container.setStyleSheet("QWidget { background-color: white; }")
        self.results_grid_layout = QGridLayout(self.results_container)
        self.results_grid_layout.setSpacing(10) 
        self.results_scroll_area.setWidget(self.results_container)
        results_frame_layout.addWidget(self.results_scroll_area, 1) # Give it stretch factor within the frame
        
        root.addWidget(self.results_background_frame, 1) # Add the new frame to the root layout, give it stretch

        # --- Pagination Controls ---
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

        # Styling for the main page (h1)
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

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
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

        top_n = self.top_spin.value()

        results, total_cv_scan, timings = perform_search(keywords, self.selected_algorithm, top_n)
        self.all_results = results 
        self.current_page = 0 

        self.exec_time_lbl.setText(
            f"Exact Search Time ({self.selected_algorithm}): {timings['exact_ms']:.2f} ms"
            f" | Fuzzy Match: {timings['fuzzy_ms']:.2f} ms"
        )
        self.total_cv_lbl.setText(f"Total CVs Processed: {total_cv_scan}")

        self._populate_current_page_results()
        self._update_pagination_buttons()

    def _populate_current_page_results(self):
        self._clear_grid_layout()

        start_index = self.current_page * self.results_per_page
        end_index = start_index + self.results_per_page
        current_page_results = self.all_results[start_index:end_index]

        num_cols = 5 # As per your requirement for 5 columns
        min_rows_to_display = 2 # To ensure a minimum height of 2 rows (for 10 results_per_page)
        
        # Calculate how many total slots we need to fill to maintain the minimum visual size
        # This will be either the actual number of results, or enough to fill min_rows_to_display * num_cols
        total_slots_to_fill = max(len(current_page_results), min_rows_to_display * num_cols)

        if not current_page_results and total_slots_to_fill == 0:
            # Handle the case where there are truly no results and no minimum size is enforced
            no_results_label = QLabel("No results found for the given keywords. Try different keywords.")
            no_results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_results_label.setStyleSheet("color: #888; font-style: italic; font-size: 16px;")
            no_results_label.setWordWrap(True)

            self.results_grid_layout.addWidget(no_results_label, 0, 0, 1, num_cols, Qt.AlignmentFlag.AlignCenter)
            self.results_grid_layout.setRowStretch(0, 1)
            self.results_grid_layout.setColumnStretch(0, 1)
            return
        elif not current_page_results:
            # If no actual results, but we still want to maintain the grid size
            # Display the message in the first cell, spanning all columns
            no_results_label = QLabel("No results found for the given keywords. Try different keywords.")
            no_results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_results_label.setStyleSheet("color: #888; font-style: italic; font-size: 16px;")
            no_results_label.setWordWrap(True)
            self.results_grid_layout.addWidget(no_results_label, 0, 0, min_rows_to_display, num_cols, Qt.AlignmentFlag.AlignCenter)
            
            # Ensure proper stretching for the empty state
            for i in range(num_cols):
                self.results_grid_layout.setColumnStretch(i, 1)
            for i in range(min_rows_to_display):
                self.results_grid_layout.setRowStretch(i, 1)
            return


        row, col = 0, 0
        for i in range(total_slots_to_fill):
            if i < len(current_page_results):
                res = current_page_results[i]
                card = ResultCard(res)
                card.summary_clicked.connect(partial(self.summary_requested.emit, res))
                card.view_cv_clicked.connect(partial(self.view_cv_requested.emit, res.get("name", "N/A"), res.get("cv_content", "CV content not available.")))
                self.results_grid_layout.addWidget(card, row, col)
            else:
                # Add an empty placeholder widget
                placeholder_widget = QWidget()
                # You can add styling here if you want empty slots to be visible, e.g.:
                # placeholder_widget.setStyleSheet("background-color: #f8f8f8; border: 1px dashed #eee; border-radius: 8px;")
                placeholder_widget.setMinimumSize(150, 100) # Give it a minimum size based on card size
                placeholder_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                self.results_grid_layout.addWidget(placeholder_widget, row, col)
            
            col += 1
            if col >= num_cols:
                col = 0
                row += 1

        # Set column and row stretches to ensure even distribution and maintain minimum height
        for i in range(num_cols):
            self.results_grid_layout.setColumnStretch(i, 1)
        
        # Ensure all rows (up to min_rows_to_display) get a stretch factor
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
