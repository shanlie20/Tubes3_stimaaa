# search.py
import time
import os

from src.utils.timer import start_timer, stop_timer
from typing import List, Tuple

from src.db.database import get_db_session
from src.db.models import ApplicantProfile, ApplicationDetail  # Importing models
from src.db.seeder import PROJECT_ROOT

from .kmp import kmp_search
from .boyer_moore import boyer_moore_search
from .aho_corasick import aho_corasick_search 
from .levenshtein import fuzzy_search

from .pdf_parser import parse_pdf_to_text  # Assumed to exist for PDF extraction

from .summary import get_candidate_summary  # Importing summary function

# untuk testing saja
from itertools import islice


def normalize_text(text: str) -> str:
    """Normalizes text by converting to lowercase and replacing non-alphanumeric characters with spaces."""
    return ''.join([char.lower() if char.isalnum() else ' ' for char in text])

# def stop_timer(start_time, action_description=""):
#     """Function to calculate and return execution time in milliseconds."""
#     end_time = time.time()
#     elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds
#     print(f"{action_description}: {elapsed_time:.2f} ms")
#     return elapsed_time

def perform_search(keywords: List[str], selected_algorithm: str, top_n: int) -> Tuple[List[dict], int, dict]:
    """
    This function performs CV search based on keywords using the selected algorithm.
    It returns three variables: search results, total scanned CVs, and execution time in a dictionary format.
    """
    results = []
    timings = {"exact_ms": 0, "fuzzy_ms": 0}
    total_cv_scan = 0

    # Start timing the search
    search_start_time = time.time()

    with get_db_session() as db:
        # Retrieve all application data with existing CVs from the database
        applicants = db.query(ApplicantProfile, ApplicationDetail).join(ApplicationDetail).all()

        applicant_matches = []  # Stores candidate match results
        total_cv_scan = len(applicants)  # Total CVs processed

        for applicant_profile, application in islice(applicants, 4):
        # for applicant_profile, application in applicants:
            cv_path = application.cv_path # CV file path
            applicant_id = applicant_profile.applicant_id
            first_name = applicant_profile.first_name

            # print(f"cv_path: {cv_path}")  # Debugging output to see CV path
            full_cv_path = os.path.join(PROJECT_ROOT, "data", cv_path)
            cv_content = ""
            if os.path.exists(full_cv_path):
                try:
                    cv_content = parse_pdf_to_text(full_cv_path) 
                    # print(f"cv_content (first 100 chars): {cv_content[:100]}...") # Debugging output
                except Exception as e:
                    print(f"Error parsing PDF {full_cv_path}: {e}")
                    cv_content = "" # Ensure cv_content is empty on error
            else:
                print(f"File {cv_path} not found at {full_cv_path}.")
            
            # print("iteration :", applicant_id)  # Debugging output to see iteration
            # Normalize CV text
            normalized_cv_content = normalize_text(cv_content)

            match_count = 0
            matched_keywords_detail = {} # Stores matched keyword pairs along with their occurrence counts

            normalized_keywords = [normalize_text(keyword) for keyword in keywords]
            if(selected_algorithm == "Aho-Corasick"):
                start_time = start_timer()
                print(f"normalized_keywords: {normalized_keywords}")  # Debugging output
                matched_keywords_detail = aho_corasick_search(normalized_keywords, normalized_cv_content)
                match_count = sum(matched_keywords_detail.values())
                exec_time_exact = stop_timer(start_time, f"Aho-Corasick Search for {len(normalized_keywords)} keywords")
                print(f"match_count (Aho-Corasick): {match_count}")  # Debugging output

            else:
                for keyword in keywords:
                    # Normalize keyword
                    normalized_keyword = normalize_text(keyword)

                    current_keyword_occurrences = 0

                    # Selected matching algorithm
                    if selected_algorithm == "KMP":
                        start_time = start_timer()
                        current_keyword_occurrences = kmp_search(normalized_cv_content, normalized_keyword)
                        exec_time_exact = stop_timer(start_time, f"{selected_algorithm} Search for '{normalized_keyword}'")

                    elif selected_algorithm == "Boyer-Moore":
                        start_time = start_timer()
                        current_keyword_occurrences = boyer_moore_search(normalized_cv_content, normalized_keyword)
                        exec_time_exact = stop_timer(start_time, f"{selected_algorithm} Search for '{normalized_keyword}'")
                        # print("current_keyword_occurrences (Boyer-Moore):", current_keyword_occurrences)  # Debugging output

                    # elif selected_algorithm == "Aho-Corasick":
                    #     current_keyword_occurrences = aho_corasick_search(normalized_cv_content, normalized_keyword)
                    else:
                        # Default Python string search (if no algorithm is selected or invalid)
                        current_keyword_occurrences = normalized_cv_content.count(normalized_keyword)

                    # If there are matches, add to total and store detail
                    if current_keyword_occurrences > 0:
                        match_count += current_keyword_occurrences
                        matched_keywords_detail[keyword] = current_keyword_occurrences

                    # If no exact match, check for fuzzy matches (typos)
                    else :
                        start_time = start_timer()
                        current_keyword_occurrences = fuzzy_search(normalized_cv_content, normalized_keyword, threshold=0.8)
                        exec_time_fuzzy = stop_timer(start_time, f"Fuzzy Search for '{normalized_keyword}'")
                        if current_keyword_occurrences > 0:
                            match_count += current_keyword_occurrences
                            typo_keyword = f"{keyword} (typo)"
                            matched_keywords_detail[typo_keyword] = current_keyword_occurrences  
                            
                    timings["exact_ms"] += exec_time_exact if 'exec_time_exact' in locals() else 0
                    timings["fuzzy_ms"] += exec_time_fuzzy if 'exec_time_fuzzy' in locals() else 0

            # Save results if there are any matches for the applicant
            if match_count > 0:
                applicant_matches.append({
                    "name": first_name,
                    "matched_keywords_detail": matched_keywords_detail, # Dictionary of keywords to their counts
                    "total_matches": match_count,
                    "applicant_id": applicant_id,
                    "cv_path": full_cv_path, # Store the full path to the CV
                    "cv_content": cv_content # Store the extracted CV text for summary/view
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
