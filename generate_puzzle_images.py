"""
generate_puzzle_images.py
--------------------------
Creates placeholder PNG puzzle images for the demo.
Run this script once locally (or in the container) to populate static/puzzles/.

Usage:
    python generate_puzzle_images.py
"""

import os
import struct
import zlib


def make_png(filename: str, width: int, height: int, color: tuple, label: str = None):
    """
    Create a simple solid-color PNG file with an optional color-coded label area.
    No external libraries required — uses raw PNG byte construction.
    """
    r, g, b = color

    # Build raw pixel rows: each row = filter byte (0) + RGB pixels
    rows = []
    for y in range(height):
        row = b"\x00"  # filter type None
        for x in range(width):
            # Draw a dark border
            if x < 4 or x >= width - 4 or y < 4 or y >= height - 4:
                row += bytes([max(0, r - 60), max(0, g - 60), max(0, b - 60)])
            # Draw a lighter pattern in the center to look like a puzzle element
            elif (x // 16 + y // 16) % 2 == 0:
                row += bytes([min(255, r + 30), min(255, g + 30), min(255, b + 30)])
            else:
                row += bytes([r, g, b])
        rows.append(row)

    raw_data = b"".join(rows)
    compressed = zlib.compress(raw_data)

    def chunk(name: bytes, data: bytes) -> bytes:
        c = name + data
        crc = zlib.crc32(c) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + c + struct.pack(">I", crc)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", compressed)
    png += chunk(b"IEND", b"")

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as f:
        f.write(png)
    print(f"Created: {filename}")


if __name__ == "__main__":
    base = "static/puzzles"

    # Color palette: distinct colors for each puzzle set
    PALETTE = {
        "pattern1": (70, 130, 180),   # Steel Blue — Pattern Recognition
        "pattern2": (60, 179, 113),   # Medium Sea Green — Spatial Awareness
        "pattern3": (186, 85, 211),   # Medium Orchid — Pattern Recognition 2
        "pattern4": (255, 140, 0),    # Dark Orange — Spatial Awareness 2
        "opt_a": (220, 80, 80),       # Red
        "opt_b": (80, 180, 80),       # Green
        "opt_c": (80, 80, 220),       # Blue
        "opt_d": (200, 160, 60),      # Gold
    }

    # Main puzzle images (128x128)
    for i in range(1, 5):
        color = PALETTE[f"pattern{i}"]
        make_png(f"{base}/pattern{i}.png", 128, 128, color)

    # Option images for each puzzle set (80x80)
    for i in range(1, 5):
        for opt in ["a", "b", "c", "d"]:
            base_color = PALETTE[f"opt_{opt}"]
            # Slightly vary the shade per puzzle set
            shade = (i - 1) * 15
            color = (
                min(255, base_color[0] + shade),
                min(255, base_color[1] + shade),
                min(255, base_color[2] - shade),
            )
            make_png(f"{base}/opt_{opt}{i}.png", 80, 80, color)

    print("\nAll puzzle images created in static/puzzles/")
