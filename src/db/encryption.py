from src.core.encryption import encrypt
from src.db.models import ApplicantProfile, ApplicationDetail
from src.db.database import get_db_session

# Fungsi untuk mengenkripsi data yang ada di tabel ApplicantProfile dan ApplicationDetail
def encrypt_all_data():

    with get_db_session() as db:
        # Ambil semua data pelamar dari tabel ApplicantProfile
        applicants = db.query(ApplicantProfile).all()

        for applicant in applicants:
            # Mengenkripsi data yang sensitif
            encrypted_first_name = encrypt(applicant.first_name)
            encrypted_last_name = encrypt(applicant.last_name)
            encrypted_date_of_birth = encrypt(str(applicant.date_of_birth))
            encrypted_address = encrypt(applicant.address)
            encrypted_phone_number = encrypt(applicant.phone_number)

            # Memperbarui data yang sudah terenkripsi di ApplicantProfile
            applicant.first_name = encrypted_first_name
            applicant.last_name = encrypted_last_name
            applicant.phone_number = encrypted_phone_number
            applicant.address = encrypted_address
            applicant.date_of_birth = encrypted_date_of_birth

        # Commit perubahan di ApplicantProfile
        db.commit()

        # Commit perubahan di ApplicationDetail
        db.commit()

        print("Semua data telah berhasil dienkripsi dan diperbarui.")

if __name__ == "__main__":
    encrypt_all_data()
    print("Proses enkripsi data selesai.")