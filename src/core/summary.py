from src.db.database import get_db_session
from src.db.models import ApplicantProfile, ApplicationDetail

def get_candidate_summary(applicant_id: int) -> dict:
    """
    Mengambil summary kandidat berdasarkan applicant_id yang diberikan
    dengan menggabungkan data dari applicantprofile dan applicationdetail.
    """
    with get_db_session() as db:
        result = db.query(ApplicantProfile, ApplicationDetail) \
                   .join(ApplicationDetail, ApplicantProfile.applicant_id == ApplicationDetail.applicant_id) \
                   .filter(ApplicantProfile.applicant_id == applicant_id) \
                   .first()  # Hanya ambil satu karena applicant_id unik

        if result:
            applicant_profile, application_detail = result

            summary_data = {
                "applicant_id": applicant_profile.applicant_id,
                "first_name": applicant_profile.first_name,
                "last_name": applicant_profile.last_name,
                "date_of_birth": applicant_profile.date_of_birth,
                "address": applicant_profile.address,
                "phone_number": applicant_profile.phone_number,
                "role": application_detail.application_role,
            }

            return summary_data
        else:
            return {}

# # Contoh penggunaan
# applicant_id = 1  # ID kandidat yang ingin diambil summary-nya
# candidate_summary = get_candidate_summary(applicant_id)
# print(candidate_summary)
