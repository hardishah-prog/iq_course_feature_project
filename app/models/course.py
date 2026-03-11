"""
models/course.py
----------------
SQLAlchemy ORM model for a Course.

A Course is the top-level learning unit that belongs to a cognitive area
and has a difficulty level.
"""

from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class CognitiveArea(str, enum.Enum):
    analytical_reasoning = "Analytical Reasoning"
    pattern_recognition = "Pattern Recognition"
    spatial_awareness = "Spatial Awareness"
    logical_thinking = "Logical Thinking"
    memory_evaluation = "Memory Evaluation"


class DifficultyLevel(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    cognitive_area = Column(
        SAEnum(CognitiveArea, name="cognitive_area_enum", create_type=True),
        nullable=False
    )
    difficulty = Column(
        SAEnum(DifficultyLevel, name="difficulty_enum", create_type=True),
        nullable=False
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    # One course has many lessons
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
