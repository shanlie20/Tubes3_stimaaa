from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text 
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class ApplicantProfile(Base):
    __tablename__ = "ApplicantProfile"
    applicant_id = Column(Integer, primary_key=True, nullable=False, autoincrement=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    address = Column(String(255), nullable=True) 
    phone_number = Column(String(20), nullable=True)
    applications = relationship("ApplicationDetail", back_populates="applicant", cascade="all, delete-orphan")
    def __repr__(self):
        full_name = []
        if self.first_name:
            full_name.append(self.first_name)
        if self.last_name:
            full_name.append(self.last_name)
        return f"<ApplicantProfile(applicant_id={self.applicant_id}, name='{' '.join(full_name)}')>"

class ApplicationDetail(Base):
    __tablename__ = "ApplicationDetail"
    detail_id = Column(Integer, primary_key=True, nullable=False, autoincrement=False)
    applicant_id = Column(Integer, ForeignKey("ApplicantProfile.applicant_id", ondelete="CASCADE"), nullable=False)
    application_role = Column(String(100), nullable=True)
    applicant = relationship("ApplicantProfile", back_populates="applications")
    def __repr__(self):
        return f"<ApplicationDetail(detail_id={self.detail_id}, applicant_id={self.applicant_id}, role='{self.application_role}')>"