import os
from functools import lru_cache

from src.utils.timer import start_timer, stop_timer
from typing import List, Tuple, Dict

from src.db.database import get_db_session
from src.db.models import ApplicantProfile, ApplicationDetail

from .kmp import kmp_search
from .boyer_moore import boyer_moore_search
from .aho_corasick import aho_corasick_search
from .levenshtein import fuzzy_search
from .encryption import decrypt

from src.core.pdf_parser import parse_pdf_to_text_and_extract_info

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def normalize_text(text: str) -> str:
    normalized = ''.join([char.lower() if char.isalnum() else ' ' for char in text])
    return ' '.join(normalized.split())

@lru_cache(maxsize=64)
def perform_search(keywords_tuple: Tuple[str, ...], selected_algorithm: str, top_n: int) -> Tuple[List[Dict], int, Dict]:
    results = []
    timings = {"exact_ms": 0.0, "fuzzy_ms": 0.0}
    
    normalized_keywords_input = [normalize_text(keyword) for keyword in keywords_tuple]

    with get_db_session() as db:
        applicants_query = db.query(ApplicantProfile, ApplicationDetail).join(
            ApplicationDetail, ApplicantProfile.applicant_id == ApplicationDetail.applicant_id
        )
        all_applicants = applicants_query.all()
        total_cv_scan = len(all_applicants)
        applicant_matches = []

        for applicant_profile, application in all_applicants:
            cv_path = application.cv_path
            applicant_id = applicant_profile.applicant_id
            
            # Panggil decrypt() tetap ada sesuai permintaan Anda
            full_name = f"{decrypt(applicant_profile.first_name)} {decrypt(applicant_profile.last_name)}".strip()

            cv_content = ""
            extracted_skills = []
            extracted_job_history = []
            extracted_education = []

            full_cv_path = os.path.join(PROJECT_ROOT, cv_path)
            if os.path.exists(full_cv_path):
                try:
                    # Parsing dan ekstraksi info dilakukan setiap saat
                    extracted_cv_data = parse_pdf_to_text_and_extract_info(full_cv_path)
                    cv_content = extracted_cv_data["full_text_normalized"]
                    extracted_skills = extracted_cv_data.get("skills", [])
                    extracted_job_history = extracted_cv_data.get("job_history", [])
                    extracted_education = extracted_cv_data.get("education", [])
                except Exception as e:
                    print(f"Error parsing PDF '{full_cv_path}': {e}")
                    continue # Lanjut ke CV berikutnya jika parsing gagal
            else:
                print(f"File CV tidak ditemukan di '{full_cv_path}'.")
                continue # Lanjut ke CV berikutnya

            # Lakukan pencarian pada cv_content yang baru saja di-parsing
            normalized_cv_content = normalize_text(cv_content)

            current_applicant_total_matches = 0
            current_applicant_matched_keywords_detail = {}

            exact_match_timer_start = start_timer()
            
            if selected_algorithm == "Aho-Corasick":
                results_from_algo = aho_corasick_search(normalized_keywords_input, normalized_cv_content)
                current_applicant_matched_keywords_detail.update(results_from_algo)
                current_applicant_total_matches = sum(results_from_algo.values())
            else:
                for original_keyword, normalized_keyword in zip(keywords_tuple, normalized_keywords_input):
                    current_keyword_occurrences = 0
                    if selected_algorithm == "KMP":
                        current_keyword_occurrences = kmp_search(normalized_cv_content, normalized_keyword)
                    elif selected_algorithm == "Boyer-Moore":
                        current_keyword_occurrences = boyer_moore_search(normalized_cv_content, normalized_keyword)
                    else:
                        current_keyword_occurrences = normalized_cv_content.count(normalized_keyword)
                    
                    if current_keyword_occurrences > 0:
                        current_applicant_total_matches += current_keyword_occurrences
                        current_applicant_matched_keywords_detail[original_keyword] = current_keyword_occurrences
            
            timings["exact_ms"] += stop_timer(exact_match_timer_start, f"Exact Match for Applicant {applicant_id} using {selected_algorithm}")

            fuzzy_match_timer_start = start_timer()
            fuzzy_match_processed_for_this_applicant = False

            if selected_algorithm != "Aho-Corasick":
                for original_keyword, normalized_keyword in zip(keywords_tuple, normalized_keywords_input):
                    if original_keyword not in current_applicant_matched_keywords_detail:
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
                    "cv_content": cv_content, 
                    "skills": extracted_skills,
                    "job_history": extracted_job_history,
                    "education": extracted_education
                })

    applicant_matches.sort(key=lambda x: x["total_matches"], reverse=True)
    results = applicant_matches[:top_n]
    
    return results, total_cv_scan, timings
