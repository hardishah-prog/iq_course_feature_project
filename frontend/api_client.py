"""
api_client.py
-------------
Centralized helper for calling the Cognitive Training Platform API.
All pages import from here — no raw requests calls scattered in pages.
"""

import requests

BASE_URL = "http://localhost:8005"


def _fmt_detail(detail):
    """Format FastAPI error detail — can be a string or a list of Pydantic errors."""
    if isinstance(detail, list):
        return "; ".join(
            f"{'.'.join(str(p) for p in e.get('loc', []))}: {e.get('msg', '')}"
            for e in detail
        )
    return str(detail)


def _get(path: str, params: dict = None):
    try:
        r = requests.get(f"{BASE_URL}{path}", params=params, timeout=10)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "❌ Cannot connect to API. Is the backend running at localhost:8005?"
    except requests.exceptions.HTTPError as e:
        detail = e.response.json().get("detail", str(e))
        return None, f"❌ API Error {e.response.status_code}: {_fmt_detail(detail)}"
    except Exception as e:
        return None, f"❌ Unexpected error: {str(e)}"


def _post(path: str, payload: dict):
    try:
        r = requests.post(f"{BASE_URL}{path}", json=payload, timeout=30)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "❌ Cannot connect to API. Is the backend running at localhost:8005?"
    except requests.exceptions.HTTPError as e:
        detail = e.response.json().get("detail", str(e))
        return None, f"❌ API Error {e.response.status_code}: {_fmt_detail(detail)}"
    except Exception as e:
        return None, f"❌ Unexpected error: {str(e)}"


# ── Courses ────────────────────────────────────────────────────────────────────

def get_courses():
    return _get("/courses/")


def create_course(title: str, description: str, cognitive_area: str, difficulty: str):
    return _post("/courses/", {
        "title": title,
        "description": description,
        "cognitive_area": cognitive_area,
        "difficulty": difficulty,
    })


def get_course(course_id: int):
    return _get(f"/courses/{course_id}")


# ── Lessons ────────────────────────────────────────────────────────────────────

def get_lessons(course_id: int):
    return _get(f"/courses/{course_id}/lessons")


def create_lesson(course_id: int, title: str, content_text: str = None, image_url: str = None):
    return _post("/lessons", {
        "course_id": course_id,
        "title": title,
        "content_text": content_text,
        "image_url": image_url,
    })


# ── Quiz ───────────────────────────────────────────────────────────────────────

def get_questions(lesson_id: int):
    return _get(f"/lessons/{lesson_id}/questions")


def submit_answer(question_id: int, option_id: int):
    return _post("/submit-answer", {
        "question_id": question_id,
        "option_id": option_id,
    })


# ── AI Generation ──────────────────────────────────────────────────────────────

def generate_lesson(topic: str, course_id: int, difficulty: str):
    return _post("/generate-lesson", {
        "topic": topic,
        "course_id": course_id,
        "difficulty": difficulty,
    })


def generate_questions(topic: str, cognitive_area: str, difficulty: str, lesson_id: int):
    return _post("/generate-questions", {
        "topic": topic,
        "cognitive_area": cognitive_area,
        "difficulty": difficulty,
        "lesson_id": lesson_id,
    })


def generate_course(topic: str, difficulty: str):
    return _post("/generate-course", {
        "topic": topic,
        "difficulty": difficulty,
    })


def generate_image_puzzle(cognitive_area: str = "Pattern Recognition"):
    return _post("/generate-image-puzzle", {"cognitive_area": cognitive_area})


def check_puzzle_answer(puzzle_id: int, option_id: str):
    return _post("/check-puzzle-answer", {"puzzle_id": puzzle_id, "option_id": option_id})


# ── Health ─────────────────────────────────────────────────────────────────────

def health_check():
    return _get("/")
