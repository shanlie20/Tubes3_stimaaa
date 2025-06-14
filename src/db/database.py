
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os
from dotenv import load_dotenv
from .models import Base 

load_dotenv() 
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password") 
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3307") 
DB_NAME = os.getenv("DB_NAME", "ats_db") 
SERVER_ENGINE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"
DATABASE_URL = f"{SERVER_ENGINE_URL}/{DB_NAME}"
engine = None 
SessionLocal = None 

def initialize_engine_and_session():
    global engine, SessionLocal
    if engine is None:
        engine = create_engine(DATABASE_URL, echo=False)
    if SessionLocal is None:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def ensure_database_exists_and_recreate_if_needed(drop_if_exists: bool = False):
    global engine, SessionLocal 
    engine = None # Reset engine agar bisa dibuat ulang setelah DB mungkin di-drop
    SessionLocal = None # Reset SessionLocal

    try:
        server_engine = create_engine(SERVER_ENGINE_URL, echo=False)
        with server_engine.connect() as connection:
            if drop_if_exists:
                print(f"PERINGATAN: Akan melakukan DROP DATABASE IF EXISTS untuk '{DB_NAME}'...")
                connection.execute(text(f"DROP DATABASE IF EXISTS {DB_NAME}"))
                print(f"Database '{DB_NAME}' berhasil di-drop (jika ada sebelumnya).")
            connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            connection.commit()
            print(f"Database '{DB_NAME}' siap digunakan atau berhasil dibuat/dibuat ulang.")
        server_engine.dispose()
        initialize_engine_and_session() # Inisialisasi engine dan SessionLocal yang menunjuk ke DB_NAME
        return True
    except Exception as e:
        print(f"Error saat proses database '{DB_NAME}': {e}")
        return False

def create_tables_in_db():
    try:
        if engine is None: # Pastikan engine sudah terinisialisasi
            initialize_engine_and_session()
            if engine is None: # Jika masih None setelah coba inisialisasi
                 print("FATAL: Engine utama tidak bisa diinisialisasi. Tidak bisa membuat tabel.")
                 return
        Base.metadata.create_all(bind=engine)
        print(f"Tabel berhasil dibuat (atau sudah ada) di database '{DB_NAME}'.")
    except Exception as e:
        print(f"Error saat membuat tabel di '{DB_NAME}': {e}")
        raise
        
@contextmanager
def get_db_session():
    if SessionLocal is None:
        initialize_engine_and_session()
        if SessionLocal is None:
             raise Exception("SessionLocal tidak bisa diinisialisasi. Cek setup database.")
    db: Session = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    if ensure_database_exists_and_recreate_if_needed(drop_if_exists=True): 
        create_tables_in_db()
