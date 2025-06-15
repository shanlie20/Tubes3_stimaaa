from src.db.database import get_db_session
from src.db.models import ApplicantProfile, ApplicationDetail
from .encryption import decrypt 
from .pdf_parser import parse_pdf_to_text_and_extract_info

def get_candidate_summary(applicant_id: int, full_cv_path: str, cv_content: str = None) -> dict:
    """
    Mengambil summary kandidat berdasarkan applicant_id yang diberikan
    dengan menggabungkan data dari applicantprofile dan applicationdetail,
    serta informasi yang diekstrak (semuanya di variabel, tidak menyentuh DB).
    """
    with get_db_session() as db:
        result = db.query(ApplicantProfile, ApplicationDetail) \
                   .join(ApplicationDetail, ApplicantProfile.applicant_id == ApplicationDetail.applicant_id) \
                   .filter(ApplicantProfile.applicant_id == applicant_id) \
                   .first()

        if result:
            applicant_profile, application_detail = result

            # Langsung parsing file CV
            extracted_cv_data = parse_pdf_to_text_and_extract_info(full_cv_path)

            # Simpan hasil ekstraksi ke variabel
            extracted_skills = extracted_cv_data.get("skills", [])
            extracted_job_history = extracted_cv_data.get("job_history", [])
            extracted_education = extracted_cv_data.get("education", [])

            summary_data = {
                "applicant_id": applicant_profile.applicant_id,
                "first_name": decrypt(applicant_profile.first_name),
                "last_name": decrypt(applicant_profile.last_name),
                "date_of_birth": decrypt(applicant_profile.date_of_birth),
                "address": decrypt(applicant_profile.address),
                "phone_number": decrypt(applicant_profile.phone_number),
                "role": application_detail.application_role,
                "skills": extracted_skills,
                "job_history": extracted_job_history,   # langsung list of dicts dari hasil ekstraksi
                "education": extracted_education,       # langsung list of dicts dari hasil ekstraksi
                "cv_content": cv_content
            }
            return summary_data
        else:
            return {}

# Contoh penggunaan:
# applicant_id = 1
# full_cv_path = "data/INFORMATION-TECHNOLOGY/15118506.pdf"
# summary = get_candidate_summary(applicant_id, full_cv_path)
# print(summary)
