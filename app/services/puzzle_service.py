"""
services/puzzle_service.py
--------------------------
Returns simulated image-based cognitive puzzles from the static/puzzles/ folder.

In a production system this would call an AI image generation API.
For this demo, we use pre-defined puzzle sets served from static files.
"""

import random
from typing import Optional

# Base path for puzzle images (served by FastAPI's StaticFiles mount)
PUZZLE_BASE_URL = "/static/puzzles"

# Pool of puzzle sets — each set has a question, a main image, and 4 option images
PUZZLE_SETS = [
    {
        "puzzle_id": 1,
        "cognitive_area": "Pattern Recognition",
        "question": "Which image completes the pattern?",
        "image_url": f"{PUZZLE_BASE_URL}/pattern1.png",
        "options": [
            {"id": "a", "image_url": f"{PUZZLE_BASE_URL}/opt_a1.png", "is_correct": False},
            {"id": "b", "image_url": f"{PUZZLE_BASE_URL}/opt_b1.png", "is_correct": True},
            {"id": "c", "image_url": f"{PUZZLE_BASE_URL}/opt_c1.png", "is_correct": False},
            {"id": "d", "image_url": f"{PUZZLE_BASE_URL}/opt_d1.png", "is_correct": False},
        ],
    },
    {
        "puzzle_id": 2,
        "cognitive_area": "Spatial Awareness",
        "question": "Which shape fits in the missing space?",
        "image_url": f"{PUZZLE_BASE_URL}/pattern2.png",
        "options": [
            {"id": "a", "image_url": f"{PUZZLE_BASE_URL}/opt_a2.png", "is_correct": True},
            {"id": "b", "image_url": f"{PUZZLE_BASE_URL}/opt_b2.png", "is_correct": False},
            {"id": "c", "image_url": f"{PUZZLE_BASE_URL}/opt_c2.png", "is_correct": False},
            {"id": "d", "image_url": f"{PUZZLE_BASE_URL}/opt_d2.png", "is_correct": False},
        ],
    },
    {
        "puzzle_id": 3,
        "cognitive_area": "Pattern Recognition",
        "question": "Identify the next element in the sequence.",
        "image_url": f"{PUZZLE_BASE_URL}/pattern3.png",
        "options": [
            {"id": "a", "image_url": f"{PUZZLE_BASE_URL}/opt_a3.png", "is_correct": False},
            {"id": "b", "image_url": f"{PUZZLE_BASE_URL}/opt_b3.png", "is_correct": False},
            {"id": "c", "image_url": f"{PUZZLE_BASE_URL}/opt_c3.png", "is_correct": True},
            {"id": "d", "image_url": f"{PUZZLE_BASE_URL}/opt_d3.png", "is_correct": False},
        ],
    },
    {
        "puzzle_id": 4,
        "cognitive_area": "Spatial Awareness",
        "question": "Which 3D shape results from folding this net?",
        "image_url": f"{PUZZLE_BASE_URL}/pattern4.png",
        "options": [
            {"id": "a", "image_url": f"{PUZZLE_BASE_URL}/opt_a4.png", "is_correct": False},
            {"id": "b", "image_url": f"{PUZZLE_BASE_URL}/opt_b4.png", "is_correct": False},
            {"id": "c", "image_url": f"{PUZZLE_BASE_URL}/opt_c4.png", "is_correct": False},
            {"id": "d", "image_url": f"{PUZZLE_BASE_URL}/opt_d4.png", "is_correct": True},
        ],
    },
]


def get_random_puzzle(cognitive_area: Optional[str] = None) -> dict:
    """
    Return a random puzzle, optionally filtered by cognitive area.

    Args:
        cognitive_area: Filter by 'Pattern Recognition' or 'Spatial Awareness'.
                        If None or unrecognized, returns any random puzzle.

    Returns:
        A puzzle dict with question, image_url, and options.
    """
    if cognitive_area:
        filtered = [p for p in PUZZLE_SETS if p["cognitive_area"].lower() == cognitive_area.lower()]
        pool = filtered if filtered else PUZZLE_SETS
    else:
        pool = PUZZLE_SETS

    puzzle = random.choice(pool)

    # Return a clean response (exclude is_correct from options for the API response)
    return {
        "puzzle_id": puzzle["puzzle_id"],
        "cognitive_area": puzzle["cognitive_area"],
        "question": puzzle["question"],
        "image_url": puzzle["image_url"],
        "options": [
            {"id": opt["id"], "image_url": opt["image_url"]}
            for opt in puzzle["options"]
        ],
    }
