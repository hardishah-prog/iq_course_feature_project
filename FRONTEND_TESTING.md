# Frontend Testing Guide

This document outlines how to run the Streamlit frontend for the Cognitive Training Platform and what outputs to expect while testing its features.

## Prerequisites
Before testing the frontend, ensure the backend services (PostgreSQL, Redis, API, Worker) are running.
1. Start the backend services:
   ```bash
   docker-compose up -d
   ```
2. Verify the API is actively responding by checking `http://localhost:8005` in your browser.

## Running the Frontend
The frontend is a Streamlit application located in the `frontend/` directory.

1. Navigate to the project directory:
   ```bash
   cd /home/vraj/Documents/iq_content
   ```
2. (Optional but recommended) Create and activate a virtual environment for the frontend:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install frontend dependencies:
   ```bash
   pip install -r frontend/requirements.txt
   ```
4. Run the Streamlit application:
   ```bash
   streamlit run frontend/app.py
   ```
5. The application will start and open in your default browser, typically at `http://localhost:8501`.

---

## Testing Flow & Expected Outputs

### 1. Home Dashboard
*Location:* `frontend/app.py`
- **Action:** Open the application homepage.
- **Expected Output:**
  - A dashboard showcasing platform metrics (total courses, 5 cognitive areas, AI engine details).
  - In the sidebar, look for a green **"● API Online"** health indicator. If the backend is unreachable, this will show a red offline message.

### 2. Courses
*Location:* `frontend/pages/1_📚_Courses.py`
- **Action:** Navigate to the "Courses" page from the sidebar.
- **Expected Output:**
  - **Create a Course:** Fill the form (Title, Description, Cognitive Area, Difficulty). Upon submission, a success banner will appear with the new `Course ID`.
  - **View Courses:** The "All Courses" section dynamically updates to list your created courses, neatly displaying their details and pill-shaped badges for difficulty and category.

### 3. Lessons
*Location:* `frontend/pages/2_📖_Lessons.py`
- **Action:** Navigate to the "Lessons" page.
- **Expected Output:**
  - **Create a Lesson:** Pick a course from the dropdown, add a Lesson Title and Content Material. Upon creation, a success message will confirming insertion into the database.
  - **View Lessons:** Select an existing course from the dropdown to list all associated lessons.

### 4. Interactive Quiz
*Location:* `frontend/pages/3_🧠_Quiz.py`
- **Action:** Navigate to the "Quiz" page, pick a Course, and then choose a connected Lesson.
- **Expected Output:**
  - If questions are available for the lesson, multiple-choice questions will be displayed.
  - Select an answer for each question and click **Submit Quiz**.
  - A large **Results Box** is instantly shown displaying your correct answers fraction and percentage (e.g. `🎯 3 / 4` ~ `75%`). 
  - Expand the Answer Review panels below to see exactly which answers were right or wrong and their explanations.

### 5. AI Generation Features
*Location:* `frontend/pages/4_🤖_AI_Generate.py`
- **Action:** Explore the 4 tabs corresponding to distinct AI operations.
- **Expected Output for each Tab:**
  - **Generate Questions:** Pick a Topic, Course, and Lesson. The API enqueues a background Redis job, and the frontend instantly presents a green box containing the `Job ID`. (Questions will appear in the Quiz tab a few moments later once the background worker finishes).
  - **Generate Full Course:** Provide a course topic and difficulty. Once submitted, it outputs a `Job ID`. Upon completion, the new structure will populate your database with a Course, a new Lesson, and 3 MCQs.
  - **Generate Lesson:** Specify a topic and attach it to an existing Course to queue a job creating just one lesson.
  - **Image Puzzle:** Pick a Cognitive Area and submit. The interface will render a static mock puzzle image along with a simulated question and formatted A/B/C/D multiple-choice alternatives.
