from sqlalchemy import Column, Integer, String, Text

from .database import Base


class Consultation(Base):
    __tablename__ = "consultations"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, unique=True, index=True, nullable=False)
    diagnostic_summary = Column(Text)
    interim_care = Column(Text)
    physician_treatment = Column(Text)
    final_report = Column(Text)
