"""
services/puzzle_service.py
--------------------------
Returns simulated image-based cognitive puzzles from the static/puzzles/ folder.

Puzzle visual rules (matching generate_puzzle_images.py):
  1 — Circles Counting:    1→2→3 circles  → next = 4   (correct: D)
  2 — Growing Square:      20→36→52 px    → next = 68  (correct: C)
  3 — Fill Alternation:    filled→hollow→filled → next = hollow (correct: A)
  4 — L-Shape Rotation:    0°→90°→180°    → next = 270° (correct: B)
"""

from typing import Optional

PUZZLE_BASE_URL = "/static/puzzles"

PUZZLE_SETS = [
    {
        "puzzle_id": 1,
        "cognitive_area": "Pattern Recognition",
        "title": "Circle Count Sequence",
        "description": "The sequence shows a pattern of circles increasing one at a time.",
        "hint": "Count the circles in each step: 1 → 2 → 3 → ?",
        "question": "How many circles should appear next in the sequence?",
        "image_url": f"{PUZZLE_BASE_URL}/pattern1.png",
        "options": [
            {"id": "a", "image_url": f"{PUZZLE_BASE_URL}/opt_a1.png", "is_correct": False},
            {"id": "b", "image_url": f"{PUZZLE_BASE_URL}/opt_b1.png", "is_correct": False},
            {"id": "c", "image_url": f"{PUZZLE_BASE_URL}/opt_c1.png", "is_correct": False},
            {"id": "d", "image_url": f"{PUZZLE_BASE_URL}/opt_d1.png", "is_correct": True},
        ],
    },
    {
        "puzzle_id": 2,
        "cognitive_area": "Spatial Awareness",
        "title": "Growing Square",
        "description": "A square grows larger with each step in the sequence.",
        "hint": "The square increases in size by the same amount each step: small → medium → large → ?",
        "question": "Which square size completes the growing sequence?",
        "image_url": f"{PUZZLE_BASE_URL}/pattern2.png",
        "options": [
            {"id": "a", "image_url": f"{PUZZLE_BASE_URL}/opt_a2.png", "is_correct": False},
            {"id": "b", "image_url": f"{PUZZLE_BASE_URL}/opt_b2.png", "is_correct": False},
            {"id": "c", "image_url": f"{PUZZLE_BASE_URL}/opt_c2.png", "is_correct": True},
            {"id": "d", "image_url": f"{PUZZLE_BASE_URL}/opt_d2.png", "is_correct": False},
        ],
    },
    {
        "puzzle_id": 3,
        "cognitive_area": "Pattern Recognition",
        "title": "Filled / Hollow Alternation",
        "description": "The sequence alternates between a filled square and a hollow square outline.",
        "hint": "Filled → Hollow → Filled → ?  (the pattern alternates every step)",
        "question": "Which shape comes next in the alternating sequence?",
        "image_url": f"{PUZZLE_BASE_URL}/pattern3.png",
        "options": [
            {"id": "a", "image_url": f"{PUZZLE_BASE_URL}/opt_a3.png", "is_correct": True},
            {"id": "b", "image_url": f"{PUZZLE_BASE_URL}/opt_b3.png", "is_correct": False},
            {"id": "c", "image_url": f"{PUZZLE_BASE_URL}/opt_c3.png", "is_correct": False},
            {"id": "d", "image_url": f"{PUZZLE_BASE_URL}/opt_d3.png", "is_correct": False},
        ],
    },
    {
        "puzzle_id": 4,
        "cognitive_area": "Spatial Awareness",
        "title": "L-Shape Rotation",
        "description": "An L-shape is rotated 90° clockwise at each step.",
        "hint": "Each panel rotates the L-shape 90° clockwise: 0° → 90° → 180° → ?",
        "question": "Which orientation of the L-shape comes next after three 90° rotations?",
        "image_url": f"{PUZZLE_BASE_URL}/pattern4.png",
        "options": [
            {"id": "a", "image_url": f"{PUZZLE_BASE_URL}/opt_a4.png", "is_correct": False},
            {"id": "b", "image_url": f"{PUZZLE_BASE_URL}/opt_b4.png", "is_correct": True},
            {"id": "c", "image_url": f"{PUZZLE_BASE_URL}/opt_c4.png", "is_correct": False},
            {"id": "d", "image_url": f"{PUZZLE_BASE_URL}/opt_d4.png", "is_correct": False},
        ],
    },
]

# Quick lookup by puzzle_id for answer checking
_PUZZLE_BY_ID = {p["puzzle_id"]: p for p in PUZZLE_SETS}


def get_random_puzzle(cognitive_area: Optional[str] = None) -> dict:
    """Return a random puzzle optionally filtered by cognitive area."""
    import random
    if cognitive_area:
        filtered = [p for p in PUZZLE_SETS if p["cognitive_area"].lower() == cognitive_area.lower()]
        pool = filtered if filtered else PUZZLE_SETS
    else:
        pool = PUZZLE_SETS

    puzzle = random.choice(pool)

    return {
        "puzzle_id": puzzle["puzzle_id"],
        "cognitive_area": puzzle["cognitive_area"],
        "title": puzzle["title"],
        "description": puzzle["description"],
        "hint": puzzle["hint"],
        "question": puzzle["question"],
        "image_url": puzzle["image_url"],
        "options": [
            {"id": opt["id"], "image_url": opt["image_url"]}
            for opt in puzzle["options"]
        ],
    }


def check_puzzle_answer(puzzle_id: int, option_id: str) -> dict:
    """Check whether the selected option is correct for the given puzzle."""
    puzzle = _PUZZLE_BY_ID.get(puzzle_id)
    if not puzzle:
        return {"error": "Puzzle not found", "is_correct": False}

    correct_option = next((o for o in puzzle["options"] if o["is_correct"]), None)
    is_correct = option_id.lower() == correct_option["id"].lower() if correct_option else False

    return {
        "puzzle_id": puzzle_id,
        "selected_option": option_id,
        "is_correct": is_correct,
        "correct_option": correct_option["id"] if correct_option else None,
        "message": "✅ Correct! Well done." if is_correct else f"❌ Incorrect. The correct answer was option {correct_option['id'].upper()}." if correct_option else "❌ Could not verify.",
        "hint": puzzle["hint"],
    }
