import os
import re
from contextlib import contextmanager
from sqlalchemy import create_engine, text, text, exc
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

SERVER_ENGINE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"
DATABASE_URL = f"{SERVER_ENGINE_URL}/{DB_NAME}"

engine = None
SessionLocal = None
def initialize_engine_and_session():
    """Menginisialisasi engine dan session SQLAlchemy ke database yang sudah ada."""
    global engine, SessionLocal
    try:
        if engine is None:
            engine = create_engine(DATABASE_URL, echo=False)
        if SessionLocal is None:
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        with engine.connect() as connection:
            print(f"Koneksi ke database '{DB_NAME}' berhasil.")
    except exc.OperationalError as e:
        print(f"Gagal terhubung ke database '{DB_NAME}'. Pastikan database sudah ada dan kredensial benar.")
        print(f"Detail Error: {e}")
        raise

@contextmanager
def get_db_session():
    """Menyediakan session database yang aman untuk digunakan di aplikasi."""
    if SessionLocal is None:
        initialize_engine_and_session()
    db: Session = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def setup_database_from_sql(sql_file_path: str, drop_db_if_exists: bool = True):
    if not os.path.exists(sql_file_path):
        print(f"Error: File seeding SQL tidak ditemukan di '{sql_file_path}'")
        return
    print("Memulai proses setup database dari file SQL...")
    server_engine = create_engine(SERVER_ENGINE_URL, echo=False)
    try:
        with server_engine.connect() as connection:
            connection.execution_options(isolation_level="AUTOCOMMIT")
            if drop_db_if_exists:
                print(f"Menghapus database '{DB_NAME}' (jika ada)...")
                connection.execute(text(f"DROP DATABASE IF EXISTS {DB_NAME}"))
            print(f"Membuat database '{DB_NAME}'...")
            connection.execute(text(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
        print(f"Database '{DB_NAME}' berhasil dibuat.")
    except Exception as e:
        print(f"Gagal saat membuat database: {e}")
        return
    finally:
        server_engine.dispose()
    db_engine = create_engine(DATABASE_URL, echo=False)
    print(f"Membaca dan menjalankan skrip dari '{os.path.basename(sql_file_path)}'...")
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        commands = [cmd for cmd in sql_script.split(';') if cmd.strip()]
        with db_engine.connect() as connection:
            trans = connection.begin()
            try:
                for command in commands:
                    connection.execute(text(command))
                trans.commit()
                print("Setup database dan proses seeding dari file SQL berhasil.")
            except Exception as e:
                print(f"Error saat menjalankan perintah SQL: {e}")
                trans.rollback()
    except Exception as e:
        print(f"Gagal membaca atau mengeksekusi file SQL: {e}")
    finally:
        db_engine.dispose()

if __name__ == "__main__":
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sql_file = os.path.join(PROJECT_ROOT, "src", "db", "tubes3_seeding.sql")
    setup_database_from_sql(sql_file)