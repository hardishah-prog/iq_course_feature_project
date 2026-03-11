"""
models/option.py
----------------
SQLAlchemy ORM model for an Option (answer choice).

Each Question has multiple Options. Exactly one should have is_correct=True.
Options can have text or an image URL (for image-based MCQs).
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Option(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    option_text = Column(String(500), nullable=True)        # Text option
    option_image_url = Column(String(500), nullable=True)   # Image option (for image_mcq)
    is_correct = Column(Boolean, default=False, nullable=False)

    # Relationship back to question
    question = relationship("Question", back_populates="options")
