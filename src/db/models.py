# src/db/models.py
from sqlalchemy import create_engine, Column, Integer, String, Date, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Mapped, mapped_column
from datetime import datetime

Base = declarative_base()

class ApplicantProfile(Base):
    __tablename__ = 'ApplicantProfile'
    applicant_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(500), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(500))
    date_of_birth: Mapped[str | None] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(String(2550))
    phone_number: Mapped[str | None] = mapped_column(String(500))

class ApplicationDetail(Base):
    __tablename__ = 'ApplicationDetail'
    detail_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    applicant_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    application_role: Mapped[str | None] = mapped_column(String(100))
    cv_path: Mapped[str] = mapped_column(Text, nullable=False) 