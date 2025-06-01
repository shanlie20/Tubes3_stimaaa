# src/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os
from dotenv import load_dotenv
from models import Base 

load_dotenv() # Muat variabel dari file .env di root proyek

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password_mysql_anda") #jangan ganti password di sini
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3308") # PORT MySQL sendiri
DB_NAME = os.getenv("DB_NAME", "ats_db") # NAMA DATABASE yang dipake yang sudah ada di MySQL
DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        print(f"Tabel berhasil dibuat (atau sudah ada) di database '{DB_NAME}'.")
    except Exception as e:
        print(f"Error saat membuat tabel: {e}")
        raise

@contextmanager
def get_db_session():
    db: Session = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Menginisialisasi skema database (membuat tabel jika belum ada)...")
    init_db() # Ini akan membuat tabel berdasarkan models.py di database ats_db
    print("Inisialisasi skema database selesai.")