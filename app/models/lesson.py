"""
models/lesson.py
----------------
SQLAlchemy ORM model for a Lesson.

A Lesson belongs to a Course and contains text content and an optional image.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content_text = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)  # Optional supporting image

    # Relationships
    course = relationship("Course", back_populates="lessons")
    questions = relationship("Question", back_populates="lesson", cascade="all, delete-orphan")
