# src/db/models.py
from sqlalchemy import create_engine, Column, Integer, String, Date, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Mapped, mapped_column
from datetime import datetime

Base = declarative_base()

class ApplicantProfile(Base):
    __tablename__ = 'applicant_profiles'
    applicant_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(100))
    date_of_birth: Mapped[Date | None] = mapped_column(Date)
    address: Mapped[str | None] = mapped_column(String(255))
    phone_number: Mapped[str | None] = mapped_column(String(50))
    # Hapus email jika tidak diperlukan
    # email: Mapped[str | None] = mapped_column(String(255))

class ApplicationDetail(Base):
    __tablename__ = 'application_details'
    application_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    applicant_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    application_role: Mapped[str | None] = mapped_column(String(100))
    cv_path: Mapped[str] = mapped_column(String(255), nullable=False)
    cv_content: Mapped[str | None] = mapped_column(Text)

    # --- KOLOM BARU DENGAN TIPE STRING/TEXT BIASA (TANPA JSON) ---
    extracted_skills_str: Mapped[str | None] = mapped_column(Text) # String dipisahkan koma
    extracted_job_history_str: Mapped[str | None] = mapped_column(Text) # Simpan sebagai string yang diformat
    extracted_education_str: Mapped[str | None] = mapped_column(Text) # Simpan sebagai string yang diformat
    # --- END KOLOM BARU ---