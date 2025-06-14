import time
import os
from typing import List, Tuple
from src.db.database import get_db_session
from .kmp import kmp_search
from .boyer_moore import boyer_moore_search
from .pdf_parser import parse_pdf_to_text  # Asumsi sudah ada fungsi ini untuk ekstrak PDF
from src.db.models import ApplicantProfile, ApplicationDetail  # Mengimpor model
from src.db.seeder import PROJECT_ROOT


def normalize_text(text: str) -> str:
    """Normalisasi teks dengan mengonversi ke lowercase dan menghapus karakter non-alfabet."""
    return ''.join([char.lower() if char.isalnum() else ' ' for char in text])

def stop_timer(start_time, action_description=""):
    """Fungsi untuk menghitung dan mengembalikan waktu eksekusi dalam milidetik."""
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000  # Konversi ke milidetik
    print(f"{action_description}: {elapsed_time:.2f} ms")
    return elapsed_time

def perform_search(keywords: List[str], selected_algorithm: str, top_n: int) -> Tuple[List[dict], int, dict]:
    """
    Fungsi ini melakukan pencarian CV berdasarkan kata kunci menggunakan algoritma yang dipilih.
    Mengembalikan tiga variabel: hasil pencarian, total CV yang discan, dan waktu eksekusi dalam format dictionary.
    """
    results = []
    timings = {"exact_ms": 0, "fuzzy_ms": 0}
    total_cv_scan = 0

    # Mulai menghitung waktu pencarian
    search_start_time = time.time()

    with get_db_session() as db:
        # Ambil seluruh data aplikasi dengan CV yang ada di database
        applicants = db.query(ApplicantProfile, ApplicationDetail).join(ApplicationDetail).all()

        applicant_matches = []  # Menyimpan hasil pencocokan kandidat
        total_cv_scan = len(applicants)  # Total CV yang diproses
        for applicant_profile, application in applicants:
            cv_path = application.cv_path # Lokasi path CV
            applicant_id = applicant_profile.applicant_id
            first_name = applicant_profile.first_name

            print(f"cv_path: {cv_path}")  # Debugging output untuk melihat path CV
            full_cv_path = os.path.join(PROJECT_ROOT, "data", cv_path)
            cv_content = ""
            if os.path.exists(full_cv_path):
                    cv_content = parse_pdf_to_text(full_cv_path) 
                    print(f"cv_content: {cv_content}")
            else:
                print(f"File {cv_path} tidak ditemukan.")
            
            print("iteration :", applicant_id)  # Debugging output untuk melihat iterasi
            # Normalisasi teks CV
            normalized_cv_content = normalize_text(cv_content)

            match_count = 0
            matched_keywords = {}  # Menyimpan pasangan keyword yang cocok beserta count_occurences countnya
            for keyword in keywords:
                # Normalisasi kata kunci
                normalized_keyword = normalize_text(keyword)

                # Algoritma pencocokan yang dipilih
                if selected_algorithm == "KMP":
                    count_occurences = kmp_search(normalized_cv_content, normalized_keyword)
                elif selected_algorithm == "Boyer-Moore":
                    count_occurences = boyer_moore_search(normalized_cv_content, normalized_keyword)  # Jumlah kemunculan
                    print("count_occurences:", count_occurences)  # Debugging output
                elif selected_algorithm == "Aho-Corasick":
                    count_occurences = 0  # Placeholder untuk algoritma Aho-Corasick
                else:
                    count_occurences = [i for i in range(len(normalized_cv_content) - len(normalized_keyword) + 1)
                                   if normalized_cv_content[i:i + len(normalized_keyword)] == normalized_keyword]

                # Jika ada kecocokan, hitung jumlahnya
                if count_occurences:
                    match_count += count_occurences  # Hasil Boyer-Moore sudah berupa jumlah kemunculan
                    matched_keywords[keyword] = count_occurences  # Menyimpan jumlah kemunculan kata kunci

            # Simpan hasil jika ada kecocokan
            if match_count > 0:
                applicant_matches.append({
                    "name": first_name,
                    "matched_keywords": matched_keywords,
                    "total_matches": match_count,
                    "applicant_id": applicant_id,
                    "cv_path": cv_path
                })

        # Urutkan hasil berdasarkan jumlah kecocokan (tertinggi ke terendah)
        applicant_matches.sort(key=lambda x: x["total_matches"], reverse=True)

        # Ambil top_n hasil
        results = applicant_matches[:top_n]

    # Hitung waktu pencarian
    total_search_time = stop_timer(search_start_time, f"Total {selected_algorithm} Search")
    timings["exact_ms"] = total_search_time
    timings["fuzzy_ms"] = 0  # Placeholder jika ada fuzzy matching

    return results, total_cv_scan, timings


# #Contoh cara mengakses fungsi perform_search dan elemen-elementnya
# if __name__ == "__main__":
#     # Keywords dan algoritma yang dipilih
#     keywords = ["accounting", "python", "data analysis", "machine learning", "USA"]
#     selected_algorithm = "KMP"  # Ganti dengan "KMP", "Boyer-Moore", atau algoritma lain
#     top_n = 100

#     # Panggil fungsi pencarian
#     results, total_cv_scan, timings = perform_search(keywords, selected_algorithm, top_n)

#     # Menampilkan hasil pencarian
#     print("\nResults:")
#     for result in results:
#         print(f"Applicant ID: {result['applicant_id']}, Name: {result['name']}, Matches: {result['total_matches']}")
#         print(f"Matched Keywords: {result['matched_keywords']}")

#     # Akses jumlah kemunculan untuk kata kunci tertentu (misalnya "Python")
#     for result in results:
#         print(f"\nFor {result['name']}:")
#         for keyword in keywords:
#             if keyword in result['matched_keywords']:
#                 print(f"{keyword}: {result['matched_keywords'][keyword]} occurrences")
#             else:
#                 print(f"{keyword}: Not found")
#     print("\nAlgorithm:", selected_algorithm)
#     print("\nTotal CV Scanned:", total_cv_scan)
#     print("Execution Time (exact match):", timings["exact_ms"], "ms")
