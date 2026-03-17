# Cognitive Training Platform API Endpoints

This document outlines all the available API endpoints in the platform and explains how routes are connected.

## How Routes Are Connected

The platform uses **FastAPI** as its core web framework. The routing is structured modularly:
1. **`app/main.py`**: Acts as the central entry point. It creates the FastAPI application instance (`app = FastAPI(...)`) and includes the individual router modules using `app.include_router()`.
2. **`app/routers/`**: Contains multiple Python files (`courses.py`, `lessons.py`, `quiz.py`, `ai_generation.py`), each defining an `APIRouter`. These routers define the specific endpoint paths, HTTP methods, input schemas, and responses for their domain.

---

## 🟢 Core & Health Endpoints (`app/main.py`)

- **`GET /`**
  - **Returns**: Health check information (status, service name, auto-generated docs URL, version).
  - **Description**: Verifies the API is up and running.

- **`GET /static/{path}`**
  - **Returns**: Static files.
  - **Description**: For serving simulated image-based cognitive puzzles from the local `static/puzzles/` directory.

---

## 📚 Courses (`app/routers/courses.py`)

These endpoints manage the overarching subjects or topics. They are grouped under the `/courses` prefix.

- **`GET /courses/`**
  - **Returns**: A list of all available courses in the system.
  - **Description**: Retrieves all existing course records.

- **`POST /courses/`**
  - **Payload**: `CourseCreate` (title, description, cognitive_area, difficulty).
  - **Returns**: The newly created course object.
  - **Description**: Adds a new course to the database.

- **`GET /courses/{course_id}`**
  - **Returns**: A specific course object.
  - **Description**: Retrieves detailed information for a specific course by its unique ID.

---

## 📖 Lessons (`app/routers/lessons.py`)

Lessons belong to courses and contain the actual content text or images.

- **`GET /courses/{course_id}/lessons`**
  - **Returns**: A list of all lessons mapped to the given course ID.
  - **Description**: Useful for populating the curriculum or table of contents for a specific course.

- **`POST /lessons`**
  - **Payload**: `LessonCreate` (course_id, title, content_text, image_url).
  - **Returns**: The created lesson object.
  - **Description**: Creates a new lesson attached to a specific course.

- **`GET /lessons/{lesson_id}`**
  - **Returns**: A specific lesson.
  - **Description**: Retrieves a single lesson's details by its ID.

---

## 📝 Quizzes & Interactions (`app/routers/quiz.py`)

These endpoints handle the question-answering portion of learning.

- **`GET /lessons/{lesson_id}/questions`**
  - **Returns**: A list of Multiple Choice Questions (MCQs) and their options linked to a specific lesson.
  - **Note**: The `is_correct` field for the options is *intentionally excluded* from the response to prevent cheating or scraping answers.

- **`POST /submit-answer`**
  - **Payload**: `SubmitAnswerRequest` (question_id, option_id).
  - **Returns**: `SubmitAnswerResponse` indicating if it was correct or not, along with a message.
  - **Description**: Validates a user's chosen option against the database to check if they got the answer right.

---

## 🤖 AI Generation (`app/routers/ai_generation.py`)

These endpoints use background workers (Redis + RQ) or mock utilities to generate learning content on the fly.

- **`POST /generate-questions`**
  - **Payload**: `GenerateQuestionsRequest` (topic, cognitive_area, difficulty, lesson_id).
  - **Returns**: A success message and the enqueued `job_id`.
  - **Description**: Triggers a background job that uses the Groq API to generate 3–5 MCU questions matching the criteria, inserting them into the DB under the given lesson.

- **`POST /generate-course`**
  - **Payload**: `GenerateCourseRequest` (topic, difficulty).
  - **Returns**: A success message and the enqueued `job_id`.
  - **Description**: Triggers a background job to generate a complete course from scratch. It builds a Course record, a Lesson with AI-generated text content, and generates 3 MCQ questions.

- **`POST /generate-image-puzzle`**
  - **Payload**: `GenerateImagePuzzleRequest` (cognitive_area).
  - **Returns**: A JSON object detailing a puzzle and its image properties.
  - **Description**: For demo purposes, this pulls a random simulated image-based cognitive puzzle from the static folders. In production, this can enqueue an AI image-generation job.
