from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class ApplicantProfile(Base):
    __tablename__ = "ApplicantProfile"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nama = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    telepon = Column(String(50), nullable=True)
    alamat = Column(Text, nullable=True)
    tanggal_dibuat = Column(TIMESTAMP, server_default=func.now())
    tanggal_diperbarui = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    applications = relationship("ApplicationDetail", back_populates="applicant", cascade="all, delete-orphan")
    def __repr__(self):
        return f"<ApplicantProfile(id={self.id}, nama='{self.nama}')>"

class ApplicationDetail(Base):
    __tablename__ = "ApplicationDetail"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    applicant_id = Column(Integer, ForeignKey("ApplicantProfile.id", ondelete="CASCADE"), nullable=False)
    cv_path = Column(String(512), nullable=False)
    posisi_dilamar = Column(String(255), nullable=True)
    tanggal_unggah_cv = Column(TIMESTAMP, server_default=func.now())
    applicant = relationship("ApplicantProfile", back_populates="applications")
    def __repr__(self):
        return f"<ApplicationDetail(id={self.id}, cv_path='{self.cv_path}')>"