"""
routers/quiz.py
---------------
Quiz endpoints: fetch questions and submit answers.

GET  /lessons/{lesson_id}/questions  — get all MCQ questions for a lesson
POST /submit-answer                  — check if a chosen option is correct
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from app.database import get_db
from app.models.question import Question
from app.models.option import Option
from app.models.lesson import Lesson

router = APIRouter(tags=["Quiz"])


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class OptionResponse(BaseModel):
    id: int
    option_text: Optional[str]
    option_image_url: Optional[str]
    # NOTE: is_correct is intentionally omitted from response to avoid cheating

    class Config:
        from_attributes = True


class QuestionResponse(BaseModel):
    id: int
    question_text: str
    difficulty: str
    question_type: str
    image_url: Optional[str]
    options: List[OptionResponse]

    class Config:
        from_attributes = True


class SubmitAnswerRequest(BaseModel):
    question_id: int
    option_id: int


class SubmitAnswerResponse(BaseModel):
    is_correct: bool
    message: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/lessons/{lesson_id}/questions", response_model=List[QuestionResponse])
def get_questions(lesson_id: int, db: Session = Depends(get_db)):
    """Return all questions (with their options) for a lesson."""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    questions = (
        db.query(Question)
        .filter(Question.lesson_id == lesson_id)
        .all()
    )
    return questions


@router.post("/submit-answer", response_model=SubmitAnswerResponse)
def submit_answer(payload: SubmitAnswerRequest, db: Session = Depends(get_db)):
    """
    Submit an answer to a question.
    Returns whether the selected option is correct.
    """
    # Validate question exists
    question = db.query(Question).filter(Question.id == payload.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Validate option exists and belongs to this question
    option = (
        db.query(Option)
        .filter(Option.id == payload.option_id, Option.question_id == payload.question_id)
        .first()
    )
    if not option:
        raise HTTPException(status_code=404, detail="Option not found for this question")

    if option.is_correct:
        return SubmitAnswerResponse(is_correct=True, message="✅ Correct! Well done.")
    else:
        return SubmitAnswerResponse(is_correct=False, message="❌ Incorrect. Try again!")
