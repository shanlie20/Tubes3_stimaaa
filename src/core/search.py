import os
import time
from functools import lru_cache
import json # Pastikan ini tetap ada jika Anda menggunakan JSON di suatu tempat

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
    total_cv_scan = 0

    normalized_keywords_input = [normalize_text(keyword) for keyword in keywords_tuple]

    with get_db_session() as db:
        # --- PERBAIKAN KUERI JOIN DI SINI ---
        # Memberikan kondisi join yang eksplisit
        applicants_query = db.query(ApplicantProfile, ApplicationDetail).join(
            ApplicationDetail, ApplicantProfile.applicant_id == ApplicationDetail.applicant_id
        )
        # --- AKHIR PERBAIKAN ---

        all_applicants = applicants_query.all()
        total_cv_scan = len(all_applicants)

        applicant_matches = []

        for applicant_profile, application in all_applicants:
            cv_path = application.cv_path
            applicant_id = applicant_profile.applicant_id
            full_name = f"{decrypt(applicant_profile.first_name)} {decrypt(applicant_profile.last_name)}".strip()

            cv_content = application.cv_content
            
            extracted_skills = []
            extracted_job_history = []
            extracted_education = []

            # Periksa apakah konten CV dan kolom ekstraksi sudah ada di DB
            # (Diasumsikan extracted_skills_str, _job_history_str, _education_str sudah ada di model ApplicationDetail)
            if not application.cv_content or \
               not application.extracted_skills_str or \
               not application.extracted_job_history_str or \
               not application.extracted_education_str:
                
                full_cv_path = os.path.join(PROJECT_ROOT, cv_path)
                if os.path.exists(full_cv_path):
                    try:
                        extracted_cv_data = parse_pdf_to_text_and_extract_info(full_cv_path)
                        cv_content = extracted_cv_data["full_text_normalized"]

                        application.cv_content = extracted_cv_data["full_text_normalized"]
                        
                        # Simpan skills sebagai string yang dipisahkan koma
                        application.extracted_skills_str = ", ".join(extracted_cv_data.get("skills", []))
                        
                        # Simpan job_history sebagai string yang diformat
                        formatted_job_history = []
                        for job in extracted_cv_data.get("job_history", []):
                            role = job.get("role", "")
                            period = job.get("period", "")
                            company = job.get("company", "")
                            description = job.get("description", "") # Ambil deskripsi
                            if role or period or company or description: # Cek apakah ada konten
                                # Format sesuai dengan bagaimana Anda ingin menampilkannya di SummaryPage
                                # Saya akan menggunakan format ini untuk nanti dipecah di SummaryPage
                                formatted_job_history.append(
                                    f"ROLE: {role}|PERIOD: {period}|COMPANY: {company}|DESC: {description.replace('\n', ' ')}"
                                )
                        application.extracted_job_history_str = "||".join(formatted_job_history) # Gunakan pemisah yang jelas

                        # Simpan education sebagai string yang diformat
                        formatted_education = []
                        for edu in extracted_cv_data.get("education", []):
                            major_field = edu.get("major_field", "")
                            institution = edu.get("institution", "")
                            period = edu.get("period", "")
                            if major_field or institution or period:
                                # Format sesuai dengan bagaimana Anda ingin menampilkannya di SummaryPage
                                formatted_education.append(
                                    f"MAJOR: {major_field}|INST: {institution}|PERIOD: {period}"
                                )
                        application.extracted_education_str = "||".join(formatted_education) # Gunakan pemisah yang jelas
                        
                        # Simpan data yang diekstrak untuk penggunaan di bawah
                        extracted_skills = extracted_cv_data.get("skills", [])
                        extracted_job_history = extracted_cv_data.get("job_history", []) # Tetap dict untuk passed to UI
                        extracted_education = extracted_cv_data.get("education", []) # Tetap dict untuk passed to UI

                    except Exception as e:
                        print(f"Error parsing PDF and extracting info from '{full_cv_path}': {e}")
                        cv_content = ""
                else:
                    print(f"File {cv_path} not found at {full_cv_path}.")
            else:
                # Jika sudah ada di DB, ambil dari DB
                extracted_skills = application.extracted_skills_str.split(', ') if application.extracted_skills_str else []
                
                # --- PARSE KEMBALI STRING KE LIST OF DICTS UNTUK UI (seperti sebelumnya) ---
                # Untuk Job History
                extracted_job_history = []
                if application.extracted_job_history_str:
                    for entry_str in application.extracted_job_history_str.split("||"):
                        parts = entry_str.split("|")
                        job_dict = {}
                        for part in parts:
                            if ":" in part:
                                key, value = part.split(":", 1)
                                job_dict[key.strip().lower()] = value.strip()
                        if job_dict:
                            extracted_job_history.append(job_dict)

                # Untuk Education
                extracted_education = []
                if application.extracted_education_str:
                    for entry_str in application.extracted_education_str.split("||"):
                        parts = entry_str.split("|")
                        edu_dict = {}
                        for part in parts:
                            if ":" in part:
                                key, value = part.split(":", 1)
                                edu_dict[key.strip().lower()] = value.strip()
                        if edu_dict:
                            extracted_education.append(edu_dict)
                # --- AKHIR PARSING KEMBALI ---


            if not cv_content:
                continue

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
                    "job_history": extracted_job_history, # Dikembalikan ke list of dicts
                    "education": extracted_education # Dikembalikan ke list of dicts
                })
        
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error committing updated CV content/extracted info to database: {e}")

    applicant_matches.sort(key=lambda x: x["total_matches"], reverse=True)
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
