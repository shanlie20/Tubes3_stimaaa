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

# Import the actual core search logic and utilities
from core.kmp import kmp_search
# from core.boyer_moore import boyer_moore_search # Akan diimplementasikan nanti
# from core.aho_corasick import aho_corasick_search # Akan diimplementasikan nanti
from core.pdf_parser import parse_pdf_to_text # Asumsi fungsi ini ada untuk membaca CV
from utils.timer import start_timer, stop_timer
from utils.keyword_utils import normalize_text, tokenize_text, remove_stopwords, extract_unique_keywords
from utils.file_utils import read_file_content # Jika CV disimpan sebagai teks biasa

def perform_search(keywords: list[str], algorithm: str, top_n: int) -> tuple[list[dict], dict]:
    """
    Melakukan pencarian CV berdasarkan kata kunci menggunakan algoritma yang dipilih.
    Ini adalah placeholder yang perlu diperluas untuk membaca CV dari database atau folder.
    """
    results = []
    timings = {"exact_ms": 0, "fuzzy_ms": 0}

    # Asumsi: Anda memiliki daftar CV yang dapat diakses, misalnya dari database
    # atau dari folder tertentu. Untuk contoh ini, kita akan simulasikan
    # membaca satu CV dari file dummy.
    
    # NOTE: Anda perlu menyesuaikan bagian ini untuk membaca CV dari sumber nyata Anda
    # seperti folder CV_data atau dari database.
    
    # --- SIMULASI PEMBACAAN CV DUMMY ---
    dummy_cv_paths = [
        "core/cv1.pdf", # Pastikan path ini sesuai
        # "data/cv_example_2.pdf",
        # ... tambahkan path CV lainnya
    ]
    
    all_cv_contents = []
    for i, cv_path in enumerate(dummy_cv_paths):
        # Jika CV Anda dalam format PDF, gunakan parse_pdf_to_text
        # Jika CV Anda dalam format teks biasa, gunakan read_file_content
        try:
            # Perhatikan: parse_pdf_to_text perlu diimplementasikan di core/pdf_parser.py
            # Untuk demo, kita akan menggunakan read_file_content sebagai fallback
            # atau Anda bisa langsung mengisi string dummy
            # cv_text = parse_pdf_to_text(cv_path) 
            cv_text = read_file_content(cv_path) # Menggunakan file_utils untuk teks
            if not cv_text: # Jika gagal membaca atau file tidak ada
                 cv_text = f"Ini adalah dummy CV {i+1} untuk pengujian. Di sini ada kata {keywords[0]} dan juga {keywords[1] if len(keywords) > 1 else ''}. Programmer, Developer, Python, JavaScript."

            all_cv_contents.append({"id": i + 1, "content": cv_text, "name": f"Candidate {i + 1}"})
        except Exception as e:
            print(f"Error processing CV {cv_path}: {e}")
            continue

    # --- LOGIKA PENCARIAN BERDASARKAN ALGORITMA ---
    search_start_time = start_timer()
    
    candidate_matches = [] # Menyimpan {candidate_id, match_count, matched_keywords}

    for candidate_data in all_cv_contents:
        cv_id = candidate_data["id"]
        cv_name = candidate_data["name"]
        cv_content = candidate_data["content"]
        
        normalized_cv_content = normalize_text(cv_content) # Normalisasi CV

        current_match_count = 0
        current_matched_keywords = []

        for keyword in keywords:
            normalized_keyword = normalize_text(keyword) # Normalisasi keyword
            
            # Pilih algoritma pencarian
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
                current_matched_keywords.append(keyword)

        if current_match_count > 0:
            candidate_matches.append({
                "name": cv_name,
                "match_count": current_match_count,
                "matched_keywords": list(set(current_matched_keywords)), # Pastikan unik
                "candidate_id": cv_id,
            })
    
    # Urutkan hasil berdasarkan match_count (tertinggi ke terendah) dan ambil top_n
    candidate_matches.sort(key=lambda x: x["match_count"], reverse=True)
    results = candidate_matches[:top_n]
    
    # Hitung waktu eksekusi
    total_search_time = stop_timer(search_start_time, f"Total {algorithm} Search")
    timings["exact_ms"] = total_search_time
    # Jika Anda memiliki logika fuzzy match terpisah, hitung juga waktunya di sini
    timings["fuzzy_ms"] = 0 # Placeholder jika belum ada fuzzy logic

    return results, timings


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

        # Dapatkan algoritma yang dipilih
        selected_algorithm = ""
        for button in self.alg_group.buttons():
            if button.isChecked():
                selected_algorithm = button.text()
                break
        
        top_n = self.top_spin.value()

        # Panggil fungsi perform_search yang sudah kita implementasikan
        results, timings = perform_search(keywords, selected_algorithm, top_n)

        # update timings label
        self.exec_time_lbl.setText(
            f"Waktu Pencarian {selected_algorithm}: {timings['exact_ms']:.2f} ms"
            # Hapus atau sesuaikan fuzzy_ms jika tidak ada logika fuzzy terpisah
            # f"Exact Match: {timings['exact_ms']:.2f} ms | Fuzzy Match: {timings['fuzzy_ms']:.2f} ms"
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
            # Pastikan kunci yang digunakan di ResultCard sesuai dengan data `res`
            card = ResultCard(res) 
            card.summary_clicked.connect(partial(self.summary_requested.emit, res)) # Menggunakan partial
        
            self.results_layout.addWidget(card)

        self.results_layout.addStretch(1)