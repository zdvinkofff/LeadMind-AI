from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    original_message = Column(Text, nullable=False)

    summary = Column(Text, nullable=False)
    service_type = Column(String(100), nullable=False)
    area = Column(String(50), nullable=False)
    location = Column(String(100), nullable=False)
    timeline = Column(String(100), nullable=False)
    budget = Column(String(100), nullable=False)
    lead_score = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="Новая")

    missing_data = Column(Text, nullable=False)
    next_step = Column(Text, nullable=False)
    client_reply = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)