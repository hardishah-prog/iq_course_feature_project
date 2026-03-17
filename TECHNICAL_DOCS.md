# Cognitive Training Platform - Technical Documentation

This document explains the architecture, tools, technologies, and core functions used in the Cognitive Training Platform backend.

## 1. Architecture Overview

The project is built as a **Dockerized Microservices Architecture**. It separates the fast, user-facing API from the slow, long-running AI generation tasks.

The system consists of 4 Docker containers working together:
1. **API Container (`iq_api`)**: Runs the FastAPI web server. Handles all incoming HTTP requests instantly.
2. **Worker Container (`iq_worker`)**: Runs an RQ (Redis Queue) background process. It picks up heavy AI tasks (like generating courses via Groq LLM) so the main API doesn't freeze or timeout while waiting for AI responses.
3. **Database Container (`iq_db`)**: Runs PostgreSQL. Stores all Courses, Lessons, Questions, and Options.
4. **Redis Container (`iq_redis`)**: Acts as the message broker between the API and the Worker. When the API wants to generate a course, it puts a message in Redis. The Worker sees this message, claims it, and processes it.

---

## 2. Tools & Technologies Stack

| Technology | Purpose in this Project |
| :--- | :--- |
| **Python 3.11** | The core programming language used for both the API and Worker. |
| **FastAPI** | High-performance web framework used to build the REST API routing. |
| **Uvicorn** | The ASGI web server that actually runs the FastAPI application. |
| **PostgreSQL** | Relational database. Chosen because cognitive training data (Course -> Lesson -> Question -> Option) is highly relational. |
| **SQLAlchemy** | The Object Relational Mapper (ORM). It allows us to interact with the PostgreSQL database using Python objects instead of writing raw SQL strings (`SELECT * FROM...`). |
| **Redis** | In-memory data store. Used purely as a message queue broker. |
| **RQ (Redis Queue)** | A lightweight Python library for queueing jobs and processing them in the background with workers. |
| **Groq API** | The AI Inference provider. Groq uses specialized hardware (LPUs) to run Large Language Models (LLMs) extremely fast. |
| **Llama-3.3-70b-versatile** | The specific open-source LLM running on Groq used for generating educational content and logical multiple-choice questions. |
| **Docker & Compose** | Ensures the database, redis, api, and worker all run in identical, isolated environments regardless of what OS the developer is using. |

---

## 3. Core Modules & Functions Breakdown

### A. The Database Layer (`app/models/` & `app/database.py`)
Instead of using Alembic for complex database migrations, this demo project takes a simpler approach. In `app/main.py`, the code `Base.metadata.create_all(bind=engine)` runs on startup. This looks at all the Python classes in `app/models/` and automatically creates the corresponding SQL tables if they don't exist.

*   `Course`: Has Enums for `cognitive_area` and `difficulty`. One Course has many Lessons.
*   `Lesson`: Contains the `content_text` (the reading material). One Lesson has many Questions.
*   `Question`: Belongs to a Lesson. Has a `question_type` (text vs image). One Question has many Options.
*   `Option`: Belongs to a Question. Contains the `is_correct` boolean.

### B. The API Routers (`app/routers/`)
FastAPI uses routers to organize endpoints logically.
*   **`courses.py` & `lessons.py`**: Standard CRUD (Create, Read, Update, Delete) operations. They take Pydantic models as input to validate data before it hits the database.
*   **`quiz.py`**: Contains the critical `POST /submit-answer` logic. It checks the database to see if the chosen `option_id` has `is_correct == True` and returns a success/fail message. *Notice that the `GET /questions` endpoint purposefully strips the `is_correct` flag from the response so users can't cheat by inspecting network traffic.*
*   **`ai_generation.py`**: Very thin wrapper endpoints. When you call `/generate-course`, it simply runs `task_queue.enqueue(generate_ai_course, ...)` which puts the job in Redis and instantly returns a `job_id` to the user.

### C. The Background Workers (`app/workers/tasks.py`)
Because worker functions execute in a totally different process (and container) than FastAPI, they cannot use FastAPI's database dependency injection (`Depends(get_db)`). 
*   **`_get_db_session()`**: A special helper function inside the worker that manually builds a fresh connection to PostgreSQL for every background job.
*   **`generate_ai_questions()` & `generate_ai_course()`**: These functions wait for Groq to return JSON, parse the JSON, build SQLAlchemy model instances (like `Course`, `Lesson`, `Question`), and save them all to the database in one big `db.commit()`.

### D. The AI Integration (`app/services/ai_service.py`)
This is where the magic happens.
*   The system uses **Prompt Engineering** to force the LLM to output pure JSON.
*   It strips any markdown block formatting (like ```json ... ```) that the LLM occasionally hallucinates.
*   **Fallback Mechanism**: LLM APIs fail frequently (rate limits, network errors, decommissioned models). This file wraps the Groq call in a `try/except` block. If the API fails or the JSON is malformed, it catches the error and returns a hardcoded set of 'Logical Thinking' questions. This guarantees the background job *always* succeeds and the user *always* gets a lesson, ensuring a smooth demo experience.

### E. The Image Simulator (`generate_puzzle_images.py` & `puzzle_service.py`)
Integrating a real diffusion model (like Stable Diffusion) for image generation is slow, expensive, and requires external cloud bucket storage (S3). 
*   To bypass this for the demo, `generate_puzzle_images.py` builds raw PNG file bytes using pure Python math (`struct`, `zlib`) without any heavy libraries like OpenCV or Pillow.
*   It places these generated PNGs in `static/puzzles`.
*   FastAPI mounts this folder (`app.mount("/static", StaticFiles(...))`) so the images can be served directly via URLs.
*   `puzzle_service.py` simulates AI generation by returning random combinations of these pre-existing, static image URLs.
