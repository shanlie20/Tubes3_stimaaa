from src.db.database import get_db_session
from src.db.models import ApplicantProfile, ApplicationDetail
from .encryption import decrypt 

def get_candidate_summary(applicant_id: int) -> dict:
    """
    Mengambil summary kandidat berdasarkan applicant_id yang diberikan
    dengan menggabungkan data dari applicantprofile dan applicationdetail,
    termasuk informasi yang diekstrak (tanpa JSON).
    """
    with get_db_session() as db:
        result = db.query(ApplicantProfile, ApplicationDetail) \
                   .join(ApplicationDetail, ApplicantProfile.applicant_id == ApplicationDetail.applicant_id) \
                   .filter(ApplicantProfile.applicant_id == applicant_id) \
                   .first()

        if result:
            applicant_profile, application_detail = result

            # Ambil skills sebagai list dari string yang dipisahkan koma
            skills_list = application_detail.extracted_skills_str.split(', ') if application_detail.extracted_skills_str else []
            
            # --- PARSING KEMBALI JOB HISTORY DARI STRING KE LIST OF DICTS ---
            job_history_parsed = []
            if application_detail.extracted_job_history_str:
                for entry_str in application_detail.extracted_job_history_str.split("||"):
                    parts = entry_str.split("|")
                    job_dict = {}
                    for part in parts:
                        if ":" in part:
                            key, value = part.split(":", 1)
                            job_dict[key.strip().lower()] = value.strip() # Convert key to lowercase to match expected dict keys
                    if job_dict:
                        job_history_parsed.append(job_dict)

            # --- PARSING KEMBALI EDUCATION DARI STRING KE LIST OF DICTS ---
            education_parsed = []
            if application_detail.extracted_education_str:
                for entry_str in application_detail.extracted_education_str.split("||"):
                    parts = entry_str.split("|")
                    edu_dict = {}
                    for part in parts:
                        if ":" in part:
                            key, value = part.split(":", 1)
                            edu_dict[key.strip().lower()] = value.strip() # Convert key to lowercase
                    if edu_dict:
                        education_parsed.append(edu_dict)

            summary_data = {
                "applicant_id": applicant_profile.applicant_id,
                "first_name": decrypt(applicant_profile.first_name),
                "last_name": decrypt(applicant_profile.last_name),
                "date_of_birth": decrypt(applicant_profile.date_of_birth),
                "address": decrypt(applicant_profile.address),
                "phone_number": decrypt(applicant_profile.phone_number),
                "role": application_detail.application_role,
                "skills": skills_list,
                "job_history": job_history_parsed, # Sekarang list of dicts
                "education": education_parsed, # Sekarang list of dicts
                "cv_content": application_detail.cv_content
            }
            return summary_data
        else:
            return {}

# # Contoh penggunaan
# applicant_id = 1  # ID kandidat yang ingin diambil summary-nya
# candidate_summary = get_candidate_summary(applicant_id)
# print(candidate_summary)
