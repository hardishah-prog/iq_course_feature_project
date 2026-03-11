"""
services/ai_service.py
-----------------------
Handles all Groq API calls for AI content generation.

Functions:
  - generate_questions(): Generate 3–5 MCQ questions on a topic
  - generate_course_content(): Generate lesson text + 3 questions
"""

import os
import json
import logging
from groq import Groq

logger = logging.getLogger(__name__)

# Initialize Groq client using GROQ_API_KEY from environment
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Model to use — using llama-3.3-70b-versatile as llama3-8b is decommissioned
GROQ_MODEL = "llama-3.3-70b-versatile"


def generate_questions(topic: str, cognitive_area: str, difficulty: str) -> list[dict]:
    """
    Ask Groq to generate 3–5 MCQ questions on the given topic.

    Returns:
        List of dicts, each with keys:
          - question_text (str)
          - difficulty (str)
          - options: list of {option_text, is_correct}
    """
    prompt = f"""You are an expert cognitive training instructor.

Generate exactly 4 multiple-choice questions about "{topic}" for the cognitive area "{cognitive_area}" at {difficulty} difficulty level.

Rules:
- Each question must have exactly 4 options
- Exactly 1 option must be correct
- Questions should test {cognitive_area} skills
- Difficulty: {difficulty}

Return ONLY valid JSON in this exact format (no explanation, no markdown):
[
  {{
    "question_text": "Question here?",
    "options": [
      {{"option_text": "Option A", "is_correct": false}},
      {{"option_text": "Option B", "is_correct": true}},
      {{"option_text": "Option C", "is_correct": false}},
      {{"option_text": "Option D", "is_correct": false}}
    ]
  }}
]
"""

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000,
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown code block if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        questions = json.loads(raw)
        logger.info(f"Generated {len(questions)} questions for topic: {topic}")
        return questions

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Groq JSON response: {e}")
        return _fallback_questions(topic, difficulty)
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return _fallback_questions(topic, difficulty)


def generate_course_content(topic: str, difficulty: str) -> dict:
    """
    Ask Groq to generate a full lesson with content text and 3 questions.

    Returns:
        Dict with keys:
          - title (str)
          - cognitive_area (str)
          - lesson_title (str)
          - content_text (str)
          - questions: list of question dicts (same format as generate_questions)
    """
    prompt = f"""You are an expert cognitive training course designer.

Create a short cognitive training lesson about "{topic}" at {difficulty} difficulty.

Return ONLY valid JSON in this exact format (no explanation, no markdown):
{{
  "title": "Course title here",
  "cognitive_area": "One of: Analytical Reasoning, Pattern Recognition, Spatial Awareness, Logical Thinking, Memory Evaluation",
  "lesson_title": "Lesson title here",
  "content_text": "Lesson content paragraph of 3–5 sentences explaining the concept.",
  "questions": [
    {{
      "question_text": "Question 1?",
      "options": [
        {{"option_text": "Option A", "is_correct": false}},
        {{"option_text": "Option B", "is_correct": true}},
        {{"option_text": "Option C", "is_correct": false}},
        {{"option_text": "Option D", "is_correct": false}}
      ]
    }},
    {{
      "question_text": "Question 2?",
      "options": [
        {{"option_text": "Option A", "is_correct": true}},
        {{"option_text": "Option B", "is_correct": false}},
        {{"option_text": "Option C", "is_correct": false}},
        {{"option_text": "Option D", "is_correct": false}}
      ]
    }},
    {{
      "question_text": "Question 3?",
      "options": [
        {{"option_text": "Option A", "is_correct": false}},
        {{"option_text": "Option B", "is_correct": false}},
        {{"option_text": "Option C", "is_correct": true}},
        {{"option_text": "Option D", "is_correct": false}}
      ]
    }}
  ]
}}
"""

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=3000,
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown code block if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        course_data = json.loads(raw)
        logger.info(f"Generated course content for topic: {topic}")
        return course_data

    except Exception as e:
        logger.error(f"Groq API error generating course: {e}")
        return _fallback_course(topic, difficulty)


def _fallback_questions(topic: str, difficulty: str) -> list[dict]:
    """Fallback questions used if Groq API fails."""
    return [
        {
            "question_text": f"Which of the following best describes a key concept in {topic}?",
            "options": [
                {"option_text": "Systematic analysis of patterns", "is_correct": True},
                {"option_text": "Random guessing", "is_correct": False},
                {"option_text": "Memorization without understanding", "is_correct": False},
                {"option_text": "Ignoring logical structure", "is_correct": False},
            ],
        },
        {
            "question_text": f"At {difficulty} difficulty, what strategy is most effective for {topic}?",
            "options": [
                {"option_text": "Break problems into smaller parts", "is_correct": True},
                {"option_text": "Work on all parts simultaneously", "is_correct": False},
                {"option_text": "Skip difficult steps", "is_correct": False},
                {"option_text": "Rely only on intuition", "is_correct": False},
            ],
        },
    ]


def _fallback_course(topic: str, difficulty: str) -> dict:
    """Fallback course data used if Groq API fails."""
    return {
        "title": f"Introduction to {topic.title()}",
        "cognitive_area": "Logical Thinking",
        "lesson_title": f"Core Concepts of {topic.title()}",
        "content_text": (
            f"This lesson introduces the foundational concepts of {topic}. "
            f"Students will explore key principles and apply them through structured exercises. "
            f"The {difficulty} difficulty exercises help build cognitive skills progressively."
        ),
        "questions": _fallback_questions(topic, difficulty),
    }
