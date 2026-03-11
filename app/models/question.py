"""
models/question.py
------------------
SQLAlchemy ORM model for a Question.

A Question belongs to a Lesson and can be of type:
  - mcq       : Standard text-based multiple choice
  - image_mcq : Image-based multiple choice (pattern/spatial puzzles)
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class QuestionType(str, enum.Enum):
    mcq = "mcq"
    image_mcq = "image_mcq"


class QuestionDifficulty(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    difficulty = Column(
        SAEnum(QuestionDifficulty, name="question_difficulty_enum", create_type=True),
        nullable=False,
        default=QuestionDifficulty.medium
    )
    question_type = Column(
        SAEnum(QuestionType, name="question_type_enum", create_type=True),
        nullable=False,
        default=QuestionType.mcq
    )
    image_url = Column(String(500), nullable=True)  # Used for image_mcq type

    # Relationships
    lesson = relationship("Lesson", back_populates="questions")
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")
