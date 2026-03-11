"""
routers/lessons.py
------------------
CRUD endpoints for Lessons.

GET  /courses/{course_id}/lessons  — list all lessons in a course
POST /lessons                      — create a new lesson
GET  /lessons/{lesson_id}          — get a specific lesson
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from app.database import get_db
from app.models.lesson import Lesson
from app.models.course import Course

router = APIRouter(tags=["Lessons"])


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class LessonCreate(BaseModel):
    course_id: int
    title: str
    content_text: Optional[str] = None
    image_url: Optional[str] = None


class LessonResponse(BaseModel):
    id: int
    course_id: int
    title: str
    content_text: Optional[str]
    image_url: Optional[str]

    class Config:
        from_attributes = True


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/courses/{course_id}/lessons", response_model=List[LessonResponse])
def list_lessons(course_id: int, db: Session = Depends(get_db)):
    """Return all lessons for a given course."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return db.query(Lesson).filter(Lesson.course_id == course_id).all()


@router.post("/lessons", response_model=LessonResponse, status_code=201)
def create_lesson(payload: LessonCreate, db: Session = Depends(get_db)):
    """Create a new lesson linked to a course."""
    course = db.query(Course).filter(Course.id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    lesson = Lesson(**payload.model_dump())
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


@router.get("/lessons/{lesson_id}", response_model=LessonResponse)
def get_lesson(lesson_id: int, db: Session = Depends(get_db)):
    """Get a specific lesson by ID."""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson
