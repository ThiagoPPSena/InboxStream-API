from sqlalchemy import Column, String, DateTime, func
from src.database.base import Base

class Email(Base):
    __tablename__ = "emails"

    id = Column(String, primary_key=True, index=True)
    subject = Column(String, nullable=False)
    body = Column(String)
    category = Column(String, index=True)
    date = Column(DateTime(timezone=True), nullable=True)

    inserted_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)