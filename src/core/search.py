import os
from src.utils.timer import start_timer, stop_timer
from typing import List, Tuple

from src.db.database import get_db_session
from src.db.models import ApplicantProfile, ApplicationDetail
from src.db.seeder import PROJECT_ROOT

from .kmp import kmp_search
from .boyer_moore import boyer_moore_search
from .aho_corasick import aho_corasick_search
from .levenshtein import fuzzy_search

from .pdf_parser import parse_pdf_to_text

# Hapus islice import untuk deployment
# from itertools import islice

def normalize_text(text: str) -> str:
    """Normalizes text by converting to lowercase and replacing non-alphanumeric characters with spaces."""
    normalized = ''.join([char.lower() if char.isalnum() else ' ' for char in text])
    return ' '.join(normalized.split())

def perform_search(keywords: List[str], selected_algorithm: str, top_n: int) -> Tuple[List[dict], int, dict]:
    """
    This function performs CV search based on keywords using the selected algorithm.
    It returns three variables: search results, total scanned CVs, and execution time in a dictionary format.
    """
    results = []
    timings = {"exact_ms": 0.0, "fuzzy_ms": 0.0}
    total_cv_scan = 0

    # Normalisasi keywords input satu kali di awal
    normalized_keywords_input = [normalize_text(keyword) for keyword in keywords]

    with get_db_session() as db:
        applicants_query = db.query(ApplicantProfile, ApplicationDetail).join(ApplicationDetail)
        all_applicants = applicants_query.all()
        total_cv_scan = len(all_applicants)

        applicant_matches = []

        for applicant_profile, application in all_applicants:
            cv_path = application.cv_path
            applicant_id = applicant_profile.applicant_id
            full_name = f"{applicant_profile.first_name} {applicant_profile.last_name}".strip()

            full_cv_path = os.path.join(PROJECT_ROOT, "data", cv_path)
            cv_content = ""
            if os.path.exists(full_cv_path):
                try:
                    cv_content = parse_pdf_to_text(full_cv_path)
                except Exception as e:
                    print(f"Error parsing PDF {full_cv_path}: {e}")
                    cv_content = ""
            else:
                print(f"File {cv_path} not found at {full_cv_path}.")
            
            if not cv_content:
                continue

            normalized_cv_content = normalize_text(cv_content)

            current_applicant_total_matches = 0
            current_applicant_matched_keywords_detail = {}

            # --- Pengukuran Waktu Exact Match per CV ---
            exact_match_timer_start = start_timer() # Start timer untuk exact match

            if selected_algorithm == "Aho-Corasick":
                results_from_algo = aho_corasick_search(normalized_keywords_input, normalized_cv_content)
                current_applicant_matched_keywords_detail.update(results_from_algo)
                current_applicant_total_matches = sum(results_from_algo.values())
            else: # KMP atau Boyer-Moore
                for original_keyword, normalized_keyword in zip(keywords, normalized_keywords_input):
                    current_keyword_occurrences = 0
                    if selected_algorithm == "KMP":
                        current_keyword_occurrences = kmp_search(normalized_cv_content, normalized_keyword)
                    elif selected_algorithm == "Boyer-Moore":
                        current_keyword_occurrences = boyer_moore_search(normalized_cv_content, normalized_keyword)
                    else: # Fallback to Python's built-in if algo is unknown
                        current_keyword_occurrences = normalized_cv_content.count(normalized_keyword)
                    
                    if current_keyword_occurrences > 0:
                        current_applicant_total_matches += current_keyword_occurrences
                        current_applicant_matched_keywords_detail[original_keyword] = current_keyword_occurrences
            
            # Stop timer dan akumulasikan waktu exact match
            timings["exact_ms"] += stop_timer(exact_match_timer_start, f"Exact Match for Applicant {applicant_id} using {selected_algorithm}")

            fuzzy_match_timer_start = start_timer()
            fuzzy_match_processed_for_this_applicant = False

            if selected_algorithm != "Aho-Corasick":
                for original_keyword, normalized_keyword in zip(keywords, normalized_keywords_input):
                    if original_keyword not in current_applicant_matched_keywords_detail: # Jika belum ada exact match untuk keyword ini
                        fuzzy_occurrences = fuzzy_search(normalized_cv_content, normalized_keyword, threshold=0.8)
                        if fuzzy_occurrences > 0:
                            current_applicant_total_matches += fuzzy_occurrences
                            typo_keyword = f"{original_keyword} (typo)"
                            current_applicant_matched_keywords_detail[typo_keyword] = fuzzy_occurrences
                            fuzzy_match_processed_for_this_applicant = True
            
            if fuzzy_match_processed_for_this_applicant:
                 timings["fuzzy_ms"] += stop_timer(fuzzy_match_timer_start, f"Fuzzy Match for Applicant {applicant_id}")

            if current_applicant_total_matches > 0:
                applicant_matches.append({
                    "name": full_name,
                    "matched_keywords_detail": current_applicant_matched_keywords_detail,
                    "total_matches": current_applicant_total_matches,
                    "applicant_id": applicant_id,
                    "cv_path": full_cv_path,
                    "cv_content": cv_content
                })

    # Sort results by total_matches (highest to lowest)
    applicant_matches.sort(key=lambda x: x["total_matches"], reverse=True)

    # Get top_n results
    results = applicant_matches[:top_n]
    
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
