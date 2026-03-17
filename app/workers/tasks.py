"""
workers/tasks.py
----------------
RQ background task functions.

These functions run in the worker container, not in the API container.
They have full access to the database and AI services.

Tasks:
  - generate_ai_questions(topic, cognitive_area, difficulty, lesson_id)
  - generate_ai_course(topic, difficulty)
  - generate_image_puzzle(topic)
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.services.ai_service import generate_questions, generate_course_content, generate_lesson_content
from app.services.puzzle_service import get_random_puzzle

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _get_db_session():
    """
    Create a fresh database session for use inside background tasks.
    Worker tasks can't use the FastAPI dependency injection system,
    so we build the session manually using DATABASE_URL.
    """
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://iquser:iqpass@db:5432/iqdb")
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def generate_ai_questions(topic: str, cognitive_area: str, difficulty: str, lesson_id: int):
    """
    RQ Task: Generate MCQ questions using Groq API and save to database.

    Args:
        topic         — Topic to generate questions about
        cognitive_area — Cognitive area category
        difficulty    — easy / medium / hard
        lesson_id     — ID of the lesson to attach questions to
    """
    # Import models here to avoid circular imports in worker context
    from app.models.question import Question, QuestionType, QuestionDifficulty
    from app.models.option import Option

    logger.info(f"[Worker] Generating questions: topic={topic}, difficulty={difficulty}, lesson_id={lesson_id}")

    db = _get_db_session()
    try:
        # Call Groq API to generate questions
        questions_data = generate_questions(topic, cognitive_area, difficulty)

        saved_count = 0
        for q_data in questions_data:
            # Map difficulty string to enum value
            diff_enum = QuestionDifficulty(difficulty) if difficulty in ["easy", "medium", "hard"] else QuestionDifficulty.medium

            # Create the Question record
            question = Question(
                lesson_id=lesson_id,
                question_text=q_data["question_text"],
                difficulty=diff_enum,
                question_type=QuestionType.mcq,
            )
            db.add(question)
            db.flush()  # Get the question ID before adding options

            # Create Option records for this question
            for opt_data in q_data.get("options", []):
                option = Option(
                    question_id=question.id,
                    option_text=opt_data.get("option_text", ""),
                    is_correct=opt_data.get("is_correct", False),
                )
                db.add(option)

            saved_count += 1

        db.commit()
        logger.info(f"[Worker] Saved {saved_count} questions for lesson_id={lesson_id}")
        return {"status": "success", "questions_saved": saved_count, "lesson_id": lesson_id}

    except Exception as e:
        db.rollback()
        logger.error(f"[Worker] Error saving questions: {e}")
        raise
    finally:
        db.close()


def generate_ai_course(topic: str, difficulty: str):
    """
    RQ Task: Generate a complete course with a lesson and MCQ questions.

    Creates:
      - 1 Course record
      - 1 Lesson with AI-generated content text
      - 3 MCQ Question records with Options

    Args:
        topic      — Topic for the course
        difficulty — easy / medium / hard
    """
    # Import models here to avoid circular imports in worker context
    from app.models.course import Course, CognitiveArea, DifficultyLevel
    from app.models.lesson import Lesson
    from app.models.question import Question, QuestionType, QuestionDifficulty
    from app.models.option import Option

    logger.info(f"[Worker] Generating full course: topic={topic}, difficulty={difficulty}")

    db = _get_db_session()
    try:
        # Call Groq API to generate course content
        course_data = generate_course_content(topic, difficulty)

        # Map cognitive_area string to enum
        cognitive_area_str = course_data.get("cognitive_area", "Logical Thinking")
        cognitive_area_map = {
            "Analytical Reasoning": CognitiveArea.analytical_reasoning,
            "Pattern Recognition": CognitiveArea.pattern_recognition,
            "Spatial Awareness": CognitiveArea.spatial_awareness,
            "Logical Thinking": CognitiveArea.logical_thinking,
            "Memory Evaluation": CognitiveArea.memory_evaluation,
        }
        cognitive_area_enum = cognitive_area_map.get(cognitive_area_str, CognitiveArea.logical_thinking)
        difficulty_enum = DifficultyLevel(difficulty) if difficulty in ["easy", "medium", "hard"] else DifficultyLevel.medium

        # Create Course
        course = Course(
            title=course_data.get("title", f"Course on {topic}"),
            description=f"AI-generated course on {topic} at {difficulty} difficulty.",
            cognitive_area=cognitive_area_enum,
            difficulty=difficulty_enum,
        )
        db.add(course)
        db.flush()  # Get course ID

        # Create Lesson
        lesson = Lesson(
            course_id=course.id,
            title=course_data.get("lesson_title", f"Introduction to {topic}"),
            content_text=course_data.get("content_text", ""),
        )
        db.add(lesson)
        db.flush()  # Get lesson ID

        # Create Questions + Options
        diff_enum = QuestionDifficulty(difficulty) if difficulty in ["easy", "medium", "hard"] else QuestionDifficulty.medium
        saved_questions = 0

        for q_data in course_data.get("questions", []):
            question = Question(
                lesson_id=lesson.id,
                question_text=q_data["question_text"],
                difficulty=diff_enum,
                question_type=QuestionType.mcq,
            )
            db.add(question)
            db.flush()

            for opt_data in q_data.get("options", []):
                option = Option(
                    question_id=question.id,
                    option_text=opt_data.get("option_text", ""),
                    is_correct=opt_data.get("is_correct", False),
                )
                db.add(option)
            saved_questions += 1

        db.commit()
        logger.info(f"[Worker] Course created: course_id={course.id}, lesson_id={lesson.id}, questions={saved_questions}")

        return {
            "status": "success",
            "course_id": course.id,
            "lesson_id": lesson.id,
            "questions_saved": saved_questions,
        }

    except Exception as e:
        db.rollback()
        logger.error(f"[Worker] Error generating course: {e}")
        raise
    finally:
        db.close()


def generate_image_puzzle(cognitive_area: str = "Pattern Recognition"):
    """
    RQ Task: Generate (or return) an image-based cognitive puzzle.

    For this demo, returns a puzzle from the static pool.
    In production, this could call an AI image generation service.
    """
    logger.info(f"[Worker] Generating image puzzle for: {cognitive_area}")
    puzzle = get_random_puzzle(cognitive_area)
    return {"status": "success", "puzzle": puzzle}


def generate_ai_lesson(topic: str, course_id: int, difficulty: str):
    """
    RQ Task: Generate a single AI lesson and attach it to an existing course.

    Args:
        topic      — Topic for the lesson
        course_id  — Existing course to attach the lesson to
        difficulty — easy / medium / hard
    """
    from app.models.lesson import Lesson
    from app.models.course import Course

    logger.info(f"[Worker] Generating lesson: topic={topic}, course_id={course_id}")
    db = _get_db_session()
    try:
        # Validate course exists
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise ValueError(f"Course {course_id} not found")

        lesson_data = generate_lesson_content(topic, difficulty)

        lesson = Lesson(
            course_id=course_id,
            title=lesson_data.get("lesson_title", f"Lesson on {topic}"),
            content_text=lesson_data.get("content_text", ""),
        )
        db.add(lesson)
        db.commit()
        db.refresh(lesson)
        logger.info(f"[Worker] Lesson created: lesson_id={lesson.id}")
        return {"status": "success", "lesson_id": lesson.id, "title": lesson.title}
    except Exception as e:
        db.rollback()
        logger.error(f"[Worker] Error generating lesson: {e}")
        raise
    finally:
        db.close()
