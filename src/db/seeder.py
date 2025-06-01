import os
from database import get_db_session, init_db # init_db untuk memastikan tabel ada
from models import ApplicantProfile, ApplicationDetail # Model

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CV_BASE_PATH = os.path.join(PROJECT_ROOT, "src", "assets", "data")

def seed_database():
    print("Memastikan tabel database sudah ada sebelum seeding...")
    init_db() # Ini akan membuat tabel jika belum ada di database ats_db
    with get_db_session() as db:
        # Cek apakah sudah ada data untuk menghindari duplikasi seeding
        if db.query(ApplicantProfile).first():
            print("Database tampaknya sudah berisi data. Proses seeding dilewati.")
            return

        print("Memulai proses seeding data dari struktur folder CV...")
        total_cv_processed = 0
        # Iterasi melalui setiap item di CV_BASE_PATH 
        if not os.path.exists(CV_BASE_PATH):
            print(f"PERINGATAN: Direktori CV_BASE_PATH '{CV_BASE_PATH}' tidak ditemukan. Tidak ada data yang akan di-seed.")
            return

        for category_name in os.listdir(CV_BASE_PATH):
            category_path_on_disk = os.path.join(CV_BASE_PATH, category_name)
            if os.path.isdir(category_path_on_disk):
                print(f"Memproses kategori: {category_name}")
                # Iterasi melalui setiap file di dalam folder kategori
                for cv_filename in os.listdir(category_path_on_disk):
                    if cv_filename.lower().endswith(".pdf"):
                        cv_path_for_db = os.path.join(category_name, cv_filename)
                        applicant_name_base = os.path.splitext(cv_filename)[0].replace('_', ' ').replace('-', ' ').title()
                        applicant_name = f"{applicant_name_base}"
                        email_placeholder = f"{applicant_name_base.lower().replace(' ', '')}_{total_cv_processed + 1}@example.com"
                        print(f"  Menambahkan profil untuk: '{applicant_name}' dengan CV: '{cv_path_for_db}'")
                        profile = ApplicantProfile(
                            nama=applicant_name,
                            email=email_placeholder
                        )
                        db.add(profile)
                        db.flush() # Dapatkan ID profile sebelum membuat ApplicationDetail
                        application = ApplicationDetail(
                            applicant_id=profile.id,
                            cv_path=cv_path_for_db,
                            posisi_dilamar=category_name.replace('-', ' ').replace('_', ' ').title()
                        )
                        db.add(application)
                        total_cv_processed += 1
        try:
            db.commit()
            if total_cv_processed > 0:
                print(f"Data contoh berhasil di-seed dari {total_cv_processed} file CV.")
            else:
                print("Tidak ada file CV yang ditemukan di subdirektori kategori untuk di-seed.")
        except Exception as e:
            db.rollback()
            print(f"Terjadi error saat seeding: {e}")
            raise

if __name__ == "__main__":
    print("Menjalankan database seeder...")
    seed_database()