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
    QGridLayout,  # Added for grid layout
    QSpacerItem, # Added for flexible spacing
    QSizePolicy # Added for size policies
)

from .components.keyword_input import KeywordInput
from .components.result_card import ResultCard

# Import the actual core search logic and utilities
from src.core.kmp import kmp_search
# from core.boyer_moore import boyer_moore_search # Akan diimplementasikan nanti
# from core.aho_corasick import aho_corasick_search # Akan diimplementasikan nanti
from src.core.pdf_parser import parse_pdf_to_text # Asumsi fungsi ini ada untuk membaca CV
from src.utils.timer import start_timer, stop_timer
from src.utils.keyword_utils import normalize_text, tokenize_text, remove_stopwords, extract_unique_keywords
from src.utils.file_utils import read_file_content # Jika CV disimpan sebagai teks biasa

def perform_search(keywords: list[str], algorithm: str, top_n: int) -> tuple[list[dict], int, dict]:
    """
    Melakukan pencarian CV berdasarkan kata kunci menggunakan algoritma yang dipilih.
    Ini adalah placeholder yang perlu diperluas untuk membaca CV dari database atau folder.
    """
    results = []
    total_search_cv = 0
    timings = {"exact_ms": 0, "fuzzy_ms": 0}

    # Asumsi: Anda memiliki daftar CV yang dapat diakses, misalnya dari database
    # atau dari folder tertentu. Untuk contoh ini, kita akan simulasikan
    # membaca beberapa CV dari file dummy.
    
    # NOTE: Anda perlu menyesuaikan bagian ini untuk membaca CV dari sumber nyata Anda
    # seperti folder CV_data atau dari database.
    
    # --- SIMULASI PEMBACAAN CV DUMMY ---
    dummy_cv_paths = [
        "core/cv1.pdf", # Pastikan path ini sesuai
        "core/cv2.pdf", # Contoh CV dummy
        "core/cv3.pdf",
        "core/cv4.pdf",
        "core/cv5.pdf",
        "core/cv6.pdf",
        "core/cv7.pdf",
        "core/cv8.pdf",
        "core/cv9.pdf",
        "core/cv10.pdf",
        "core/cv11.pdf",
        "core/cv12.pdf",
        # ... tambahkan path CV lainnya
    ]
    
    all_cv_contents = []
    for i, cv_path in enumerate(dummy_cv_paths):
        try:
            # For demonstration, we'll use a dummy text if the file read fails
            cv_text = read_file_content(cv_path)
            if not cv_text:
                cv_text = f"Ini adalah dummy CV {i+1} untuk pengujian. Di sini ada kata {'Python' if i%2 == 0 else 'JavaScript'} dan juga {'React' if i%3 == 0 else 'Java'}. Programmer, Developer."

            all_cv_contents.append({"id": i + 1, "content": cv_text, "name": f"Applicant {i + 1}"})
        except Exception as e:
            print(f"Error processing CV {cv_path}: {e}")
            continue

    total_search_cv = len(all_cv_contents)

    # --- LOGIKA PENCARIAN BERDASARKAN ALGORITMA ---
    search_start_time = start_timer()
    
    candidate_matches = [] # Menyimpan {candidate_id, match_count, matched_keywords}

    for candidate_data in all_cv_contents:
        cv_id = candidate_data["id"]
        cv_name = candidate_data["name"]
        cv_content = candidate_data["content"]
        
        normalized_cv_content = normalize_text(cv_content) # Normalisasi CV

        current_match_count = 0
        current_matched_keywords = {} # Changed to dict to store counts per keyword

        for keyword in keywords:
            normalized_keyword = normalize_text(keyword) # Normalisasi keyword
            
            occurrences = []
            if algorithm == "KMP":
                occurrences = kmp_search(normalized_cv_content, normalized_keyword)
            # elif algorithm == "Boyer-Moore":
            #     occurrences = boyer_moore_search(normalized_cv_content, normalized_keyword)
            # elif algorithm == "Aho-Corasick":
            #     # Aho-Corasick biasanya lebih efisien untuk mencari banyak pola sekaligus
            #     # Anda mungkin perlu menyesuaikan pemanggilan fungsi ini
            #     occurrences = aho_corasick_search(normalized_cv_content, normalized_keyword)
            else:
                # Fallback untuk algoritma yang belum diimplementasikan
                # Anda bisa menggunakan pencarian string bawaan Python
                occurrences = [i for i in range(len(normalized_cv_content) - len(normalized_keyword) + 1)
                               if normalized_cv_content[i:i+len(normalized_keyword)] == normalized_keyword]

            if occurrences:
                current_match_count += len(occurrences)
                current_matched_keywords[keyword] = current_matched_keywords.get(keyword, 0) + len(occurrences)

        if current_match_count > 0:
            candidate_matches.append({
                "name": cv_name,
                "matched_keywords": current_matched_keywords, # Store as dict
                "total_matches": current_match_count,
                "applicant_id": cv_id,
                "cv_content": cv_content # Include content for 'View CV'
            })
    
    # Urutkan hasil berdasarkan match_count (tertinggi ke terendah) dan ambil top_n
    candidate_matches.sort(key=lambda x: x["total_matches"], reverse=True)
    results = candidate_matches[:top_n]
    
    # Hitung waktu eksekusi
    total_search_time = stop_timer(search_start_time, f"Total {algorithm} Search")
    timings["exact_ms"] = total_search_time
    timings["fuzzy_ms"] = 0 # Placeholder if no separate fuzzy logic

    return results, total_search_cv, timings


class SearchPage(QWidget):
    """Page that lets the recruiter search CVs by keyword."""

    # Adjusted signal to emit all relevant data for the summary page
    summary_requested = Signal(dict) 
    view_cv_requested = Signal(str, str) # New signal for viewing CV (applicant name, cv content)

    def __init__(self) -> None:
        super().__init__()
        self.current_page = 0
        self.results_per_page = 9 # 3 rows * 3 columns
        self.all_results = []
        self._build_ui()
        self._show_initial_message()

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
        self.top_spin.setRange(1, 480) # Max 480 matches
        self.top_spin.setValue(10)
        line.addWidget(top_label)
        line.addWidget(self.top_spin)

        root.addLayout(line)

        # -- Search button --
        self.search_btn = QPushButton("Search")
        self.search_btn.setDefault(True)
        self.search_btn.clicked.connect(self._on_search_clicked)
        root.addWidget(self.search_btn)

        # -- Summary execution time and total CVs --
        info_layout = QHBoxLayout()
        self.exec_time_lbl = QLabel("")
        self.total_cv_lbl = QLabel("")
        info_layout.addWidget(self.exec_time_lbl)
        info_layout.addStretch(1)
        info_layout.addWidget(self.total_cv_lbl)
        root.addLayout(info_layout)

        # -- Results area (Scrollable) --
        self.results_scroll_area = QScrollArea()
        self.results_scroll_area.setWidgetResizable(True)
        self.results_container = QWidget()
        self.results_grid_layout = QGridLayout(self.results_container) # Use QGridLayout
        self.results_grid_layout.setSpacing(10) # Spacing between cards
        self.results_scroll_area.setWidget(self.results_container)
        root.addWidget(self.results_scroll_area, 1) # Give it stretch factor

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

        # Styling placeholder via object names – use Qt stylesheets in main if needed

    def _show_initial_message(self):
        """Displays a message in the results area when no search has been performed."""
        # Clear any existing widgets AND spacers
        self._clear_grid_layout()
        
        message_label = QLabel("Please input keywords, top matches, and select an algorithm to perform a search.")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("color: #888; font-style: italic; font-size: 16px;")
        message_label.setWordWrap(True)
        
        # Create a single-cell layout that spans the entire grid
        # This ensures the message is truly centered
        self.results_grid_layout.addWidget(message_label, 0, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
        
        # Set the grid to have flexible sizing
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
        
        # Reset all stretches
        for i in range(self.results_grid_layout.rowCount()):
            self.results_grid_layout.setRowStretch(i, 0)
        for i in range(self.results_grid_layout.columnCount()):
            self.results_grid_layout.setColumnStretch(i, 0)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def _on_search_clicked(self):
        keywords = self.keyword_input.keywords()
        if not keywords:
            self.exec_time_lbl.setText("Masukkan minimal satu keyword!")
            self.total_cv_lbl.setText("")
            self._show_initial_message() # Show initial message again if no keywords
            return

        selected_algorithm = ""
        for button in self.alg_group.buttons():
            if button.isChecked():
                selected_algorithm = button.text()
                break
        
        top_n = self.top_spin.value()

        # Perform the search
        results, total_cv_scan, timings = perform_search(keywords, selected_algorithm, top_n)
        self.all_results = results # Store all results for pagination
        self.current_page = 0 # Reset to first page
        
        # Update timings and total CVs scanned labels
        self.exec_time_lbl.setText(
            f"Waktu Pencarian {selected_algorithm}: {timings['exact_ms']:.2f} ms"
            f" | Fuzzy Match: {timings['fuzzy_ms']:.2f} ms"
        )
        self.total_cv_lbl.setText(f"Total CV Diproses: {total_cv_scan}")

        # Populate result cards for the current page
        self._populate_current_page_results()
        self._update_pagination_buttons()

    def _populate_current_page_results(self):
        # Clear old cards and any spacers
        self._clear_grid_layout()

        start_index = self.current_page * self.results_per_page
        end_index = start_index + self.results_per_page
        current_page_results = self.all_results[start_index:end_index]

        if not current_page_results:
            # If no results, display a specific message
            no_results_label = QLabel("No results found for the given keywords. Try different keywords.")
            no_results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_results_label.setStyleSheet("color: #888; font-style: italic; font-size: 16px;")
            no_results_label.setWordWrap(True)

            # Add the label to span the entire grid for proper centering
            self.results_grid_layout.addWidget(no_results_label, 0, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
            
            # Set stretch to make it truly centered
            self.results_grid_layout.setRowStretch(0, 1)
            self.results_grid_layout.setColumnStretch(0, 1)
            return

        # Add cards in a 3-column grid
        row, col = 0, 0
        for res in current_page_results:
            card = ResultCard(res)
            card.summary_clicked.connect(partial(self.summary_requested.emit, res))
            card.view_cv_clicked.connect(partial(self.view_cv_requested.emit, res.get("name", "N/A"), res.get("cv_content", "CV content not available.")))
            
            self.results_grid_layout.addWidget(card, row, col)
            col += 1
            if col >= 3: # 3 columns per row
                col = 0
                row += 1

        # Set column stretches to ensure cards are evenly distributed
        for i in range(3):
            self.results_grid_layout.setColumnStretch(i, 1)

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

    def _next_page(self):
        total_pages = (len(self.all_results) + self.results_per_page - 1) // self.results_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self._populate_current_page_results()
            self._update_pagination_buttons()