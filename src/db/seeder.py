import os
import sys
import random
from datetime import date, timedelta
from faker import Faker

# Import sys untuk nyari path ke src/core/pdf_parser.py
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(SRC_DIR) 
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

try:
    from core.pdf_parser import extract_text_from_pdf_raw
except ImportError as e:
    print(f"ERROR: Gagal mengimpor 'extract_text_from_pdf_raw' dari core.pdf_parser: {e}")
    print("Pastikan file src/core/pdf_parser.py ada dan tidak ada error di dalamnya.")
    print("Pastikan juga direktori src/ dan src/core/ memiliki file __init__.py (bisa kosong).")
    def extract_text_from_pdf_raw(pdf_path: str) -> str | None:
        print(f"  [Dummy Fallback] extract_text_from_pdf_raw dipanggil untuk: {pdf_path}")
        if "accountant" in pdf_path.lower(): return "ACCOUNTANT\nCV akuntan."
        if "teacher" in pdf_path.lower(): return "TEACHER\nCV guru."
        return "Judul CV\nKonten CV dummy."
    
from database import get_db_session, ensure_database_exists_and_recreate_if_needed, create_tables_in_db
from models import ApplicantProfile, ApplicationDetail

fake = Faker('id_ID')
CV_BASE_PATH = os.path.join(PROJECT_ROOT, "data")
ROLES_KEYWORDS = [
    'ACCOUNTANT', 'ADVOCATE', 'AGRICULTURE', 'APPAREL', 'ARTS', 'AUTOMOBILE', 
    'AVIATION', 'BANKING', 'BPO', 'BUSINESS DEVELOPMENT', 'CHEF', 'CONSTRUCTION', 
    'CONSULTANT', 'DESIGNER', 'DIGITAL MEDIA', 'ENGINEERING', 'FINANCE', 
    'FITNESS', 'HEALTHCARE', 'HR', 'INFORMATION TECHNOLOGY', 
    'PUBLIC RELATIONS', 'SALES', 'TEACHER'
]

def get_first_significant_line(raw_text: str | None) -> str:
    if not raw_text: return ""
    lines = raw_text.splitlines()
    for line in lines:
        stripped_line = line.strip()
        if stripped_line: return stripped_line
    return ""

def determine_application_role(first_line: str) -> str | None:
    if not first_line: return None
    first_line_upper = first_line.upper()
    for role_keyword in ROLES_KEYWORDS:
        if role_keyword in first_line_upper: return role_keyword
    return None # Akan diisi "General Application" jika None nanti

def generate_fake_applicant_data(): #
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
            print("Database telah di-recreate (jika ada sebelumnya) atau baru dibuat.")
        print(f"Memulai proses seeding data dari direktori CV: {CV_BASE_PATH}...")
        total_cv_processed = 0
        if not os.path.exists(CV_BASE_PATH):
            print(f"PERINGATAN: Direktori CV '{CV_BASE_PATH}' tidak ditemukan. Tidak ada data akan di-seed.")
            return
        for cv_filename in os.listdir(CV_BASE_PATH):
            if cv_filename.lower().endswith(".pdf"):
                absolute_pdf_path = os.path.join(CV_BASE_PATH, cv_filename)
                print(f"  Memproses CV: {cv_filename}...")   
                raw_cv_text = extract_text_from_pdf_raw(absolute_pdf_path)
                first_line = get_first_significant_line(raw_cv_text)
                role_from_cv = determine_application_role(first_line)   
                if role_from_cv:
                    print(f"    -> Role terdeteksi: {role_from_cv}")
                else:
                    role_from_cv = "General Application" # Default jika tidak ada role terdeteksi
                    print(f"    -> Tidak ada role spesifik terdeteksi ('{first_line[:50]}...'). Role di-set ke '{role_from_cv}'.")
                applicant_data = generate_fake_applicant_data()         
                profile = ApplicantProfile(**applicant_data)
                db.add(profile)
                db.flush() 
                print(f"    Menambahkan profil: {applicant_data['first_name']} {applicant_data['last_name']} (ID DB: {profile.applicant_id})")
                application_data = {
                    "applicant_id": profile.applicant_id,
                    "application_role": role_from_cv,
                    "cv_path": cv_filename
                }
                application = ApplicationDetail(**application_data)
                db.add(application)
                total_cv_processed += 1     
        try:
            db.commit()
            if total_cv_processed > 0:
                print(f"Data contoh berhasil di-seed untuk {total_cv_processed} file CV.")
            else:
                print("Tidak ada file PDF yang ditemukan di direktori data untuk di-seed.")
        except Exception as e:
            db.rollback()
            print(f"Terjadi error saat seeding: {e}")
            raise

if __name__ == "__main__":
    print("Menjalankan database seeder...")
    seed_database(recreate_db=True)