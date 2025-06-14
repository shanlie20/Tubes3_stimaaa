import os
from datetime import date, timedelta
from faker import Faker
import subprocess

from .database import (
    get_db_session,
    ensure_database_exists_and_recreate_if_needed,
    create_tables_in_db,
    DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME  # <-- Impor variabel
)
from .models import ApplicantProfile, ApplicationDetail

fake = Faker('id_ID')
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CV_BASE_PATH = os.path.join(PROJECT_ROOT, "data")

ROLES_TO_ASSIGN = [
    'ACCOUNTANT', 'ADVOCATE', 'AGRICULTURE', 'APPAREL', 'ARTS', 'AUTOMOBILE', 
    'AVIATION', 'BANKING', 'BPO', 'BUSINESS DEVELOPMENT', 'CHEF', 'CONSTRUCTION', 
    'CONSULTANT', 'DESIGNER', 'DIGITAL MEDIA', 'ENGINEERING', 'FINANCE', 
    'FITNESS', 'HEALTHCARE', 'HR', 'INFORMATION TECHNOLOGY', 
    'PUBLIC RELATIONS', 'SALES', 'TEACHER'
]
ENTRIES_PER_ROLE = 20

def generate_fake_applicant_data():
    first_name = fake.first_name()
    last_name = fake.last_name()
    start_date = date.today() - timedelta(days=50*365)
    end_date = date.today() - timedelta(days=18*365)
    date_of_birth = fake.date_between(start_date=start_date, end_date=end_date)
    address = fake.address().replace('\n', ', ')
    phone_number = fake.phone_number()[:20]
    return {
        "first_name": first_name, "last_name": last_name,
        "date_of_birth": date_of_birth, "address": address,
        "phone_number": phone_number,
    }

def seed_database(recreate_db: bool = True):
    print("Memastikan database dan tabel sudah ada sebelum seeding...")
    if not ensure_database_exists_and_recreate_if_needed(drop_if_exists=recreate_db):
        print("Gagal memproses database. Proses seeding dihentikan.")
        return
    create_tables_in_db()

    with get_db_session() as db:
        if not recreate_db and db.query(ApplicantProfile).first():
            print("Database sudah berisi data dan tidak diminta recreate. Proses seeding dilewati.")
            return
        elif recreate_db:
            print("Database telah di-recreate atau baru dibuat.")
        print(f"Memulai proses seeding data dari direktori CV: {CV_BASE_PATH}...")
        if not os.path.exists(CV_BASE_PATH):
            print(f"PERINGATAN: Direktori CV '{CV_BASE_PATH}' tidak ditemukan. Tidak ada data akan di-seed.")
            return
        pdf_counter = 0
        for filename in os.listdir(CV_BASE_PATH):
            if filename.lower().endswith(".pdf"):
                role_index = (pdf_counter // ENTRIES_PER_ROLE) % len(ROLES_TO_ASSIGN)
                application_role = ROLES_TO_ASSIGN[role_index]
                print(f"  Memproses CV: {filename} -> Role: {application_role}")
                applicant_data = generate_fake_applicant_data()   
                profile = ApplicantProfile(**applicant_data)
                db.add(profile)
                db.flush()         
                print(f"    Menambahkan profil: {applicant_data['first_name']} {applicant_data['last_name']} (ID DB: {profile.applicant_id})")
                application = ApplicationDetail(
                    applicant_id=profile.applicant_id,
                    application_role=application_role,
                    cv_path=filename
                )
                db.add(application)
                pdf_counter += 1
        
        try:
            db.commit()
            if pdf_counter > 0:
                print(f"Data contoh berhasil di-seed untuk {pdf_counter} file CV.")
            else:
                print("Tidak ada file PDF yang ditemukan di direktori data untuk di-seed.")
        except Exception as e:
            db.rollback()
            print(f"Terjadi error saat seeding: {e}")
            raise

def dump_to_sql(output_filename="ats.sql"):
    print(f"\nMemulai proses dump database ke '{output_filename}'...")
    command = [
        'mysqldump',
        '--user=' + DB_USER,
        '--password=' + DB_PASSWORD,
        '--host=' + DB_HOST,
        '--port=' + DB_PORT,
        '--single-transaction', 
        '--routines',           
        '--triggers',           
        DB_NAME
    ]

    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            process = subprocess.run(
                command, 
                stdout=f,               
                stderr=subprocess.PIPE, 
                text=True,              
                check=False             
            )
        if process.returncode != 0:
            print(f"Error saat menjalankan mysqldump:")
            print(process.stderr)
            return False
        print(f"Database '{DB_NAME}' berhasil di-dump ke '{output_filename}'.")
        return True
    except FileNotFoundError:
        print("Error: Perintah 'mysqldump' tidak ditemukan.")
        print("Pastikan MySQL Client terinstal dan path-nya sudah benar.")
        return False
    except Exception as e:
        print(f"Terjadi error tak terduga saat proses dump: {e}")
        return False

if __name__ == "__main__":
    print("Menjalankan database seeder (langsung proses per file)...")
    seed_database(recreate_db=True)
    output_dir = os.path.join(PROJECT_ROOT, "src", "db", "ats.sql")
    dump_to_sql(output_dir)