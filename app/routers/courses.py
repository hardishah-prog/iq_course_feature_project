"""
routers/courses.py
------------------
CRUD endpoints for Courses.

GET  /courses           — list all courses
POST /courses           — create a new course
GET  /courses/{id}      — get a specific course
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models.course import Course, CognitiveArea, DifficultyLevel

router = APIRouter(prefix="/courses", tags=["Courses"])


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    cognitive_area: CognitiveArea
    difficulty: DifficultyLevel


class CourseResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    cognitive_area: str
    difficulty: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[CourseResponse])
def list_courses(db: Session = Depends(get_db)):
    """Return all available courses."""
    return db.query(Course).all()


@router.post("/", response_model=CourseResponse, status_code=201)
def create_course(payload: CourseCreate, db: Session = Depends(get_db)):
    """Create a new course."""
    course = Course(**payload.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    """Get a course by its ID."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course
