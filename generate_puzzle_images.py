"""
generate_puzzle_images.py
--------------------------
Generates meaningful visual-pattern PNG puzzle images for the demo.
All drawing is done with raw Python (struct + zlib) — no Pillow/OpenCV needed.

Puzzle designs:
  Puzzle 1 — "Circles Counting" (Pattern Recognition)
      Sequence shows 1, 2, 3 circles → answer: 4 circles  (correct = D)
  Puzzle 2 — "Growing Square" (Spatial Awareness)
      Sequence shows small, medium, large square → answer: extra-large square  (correct = C)
  Puzzle 3 — "Filled/Hollow Alternation" (Pattern Recognition)
      Sequence shows filled, hollow, filled square → answer: hollow  (correct = A)
  Puzzle 4 — "L-Shape Rotation" (Spatial Awareness)
      L-shape rotated 0°, 90°, 180° → answer: 270° rotation  (correct = B)

Usage:
    python generate_puzzle_images.py
"""

import os
import struct
import zlib

# ── PNG helpers ────────────────────────────────────────────────────────────────

BG  = (30, 30, 46)    # Dark background
FG  = (167, 139, 250) # Accent purple
HL  = (96, 165, 250)  # Blue highlight
RED = (248, 113, 113) # Wrong option hint
GRN = (52, 211, 153)  # Correct option hint
WHT = (220, 220, 220) # White-ish


def _chunk(name: bytes, data: bytes) -> bytes:
    c = name + data
    crc = zlib.crc32(c) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + c + struct.pack(">I", crc)


def _make_png(pixels: list, width: int, height: int) -> bytes:
    """Build a PNG from a flat list of (R,G,B) tuples, row-major."""
    rows = []
    for y in range(height):
        row = b"\x00"
        for x in range(width):
            r, g, b = pixels[y * width + x]
            row += bytes([r, g, b])
        rows.append(row)
    raw = b"".join(rows)
    png  = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(raw))
    png += _chunk(b"IEND", b"")
    return png


def save_png(path: str, pixels: list, width: int, height: int):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(_make_png(pixels, width, height))
    print(f"  Created: {path}")


# ── Drawing primitives ─────────────────────────────────────────────────────────

def blank(w, h, color=BG):
    return [color] * (w * h)


def set_pixel(pixels, w, x, y, color):
    if 0 <= x < w and 0 <= y < len(pixels) // w:
        pixels[y * w + x] = color


def fill_rect(pixels, w, x0, y0, x1, y1, color):
    for y in range(y0, y1):
        for x in range(x0, x1):
            set_pixel(pixels, w, x, y, color)


def draw_rect_border(pixels, w, x0, y0, x1, y1, color, thickness=2):
    for t in range(thickness):
        for x in range(x0 + t, x1 - t):
            set_pixel(pixels, w, x, y0 + t, color)
            set_pixel(pixels, w, x, y1 - 1 - t, color)
        for y in range(y0 + t, y1 - t):
            set_pixel(pixels, w, x0 + t, y, color)
            set_pixel(pixels, w, x1 - 1 - t, y, color)


def draw_circle(pixels, w, cx, cy, r, color):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                set_pixel(pixels, w, x, y, color)


def draw_circle_border(pixels, w, cx, cy, r, color, thickness=2):
    for y in range(cy - r - 1, cy + r + 2):
        for x in range(cx - r - 1, cx + r + 2):
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            if (r - thickness) ** 2 <= d2 <= r * r:
                set_pixel(pixels, w, x, y, color)


def divider(pixels, w, x, h, color=(60, 60, 80)):
    for y in range(h):
        set_pixel(pixels, w, x, y, color)


# ── Sequence strip (3 panels side by side) ─────────────────────────────────────

def make_sequence_strip(panel_fns, panel_w=96, panel_h=96):
    """
    panel_fns: list of 3 callables, each receives (pixels, W, pw, ph, ox)
               where ox = x-offset of this panel.
    Returns a strip image W=panel_w*3+2*dividers, H=panel_h
    """
    DIV = 3
    W = panel_w * 3 + DIV * 2
    H = panel_h
    pixels = blank(W, H)

    offsets = [0, panel_w + DIV, panel_w * 2 + DIV * 2]
    for fn, ox in zip(panel_fns, offsets):
        fn(pixels, W, panel_w, H, ox)
        if ox > 0:
            for yy in range(H):
                for dd in range(DIV):
                    set_pixel(pixels, W, ox - DIV + dd, yy, (55, 55, 75))

    # Outer border
    draw_rect_border(pixels, W, 0, 0, W, H, (80, 80, 110), 2)
    return pixels, W, H


def make_option_image(draw_fn, pw=80, ph=80):
    pixels = blank(pw, ph)
    draw_fn(pixels, pw, pw, ph, 0)
    draw_rect_border(pixels, pw, 0, 0, pw, ph, (80, 80, 110), 2)
    return pixels, pw, ph


# ═══════════════════════════════════════════════════════════════════════════════
# PUZZLE 1 — Circles Counting
#   Panel i shows i circles (1→2→3).  Correct next = 4 circles.
#   Options: A=1 circle  B=2 circles  C=3 circles  D=4 circles (correct)
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_n_circles(n, pixels, W, pw, ph, ox):
    """Draw n circles evenly distributed inside the panel at x-offset ox."""
    r = 10
    positions = {
        1: [(pw // 2, ph // 2)],
        2: [(pw // 3, ph // 2), (2 * pw // 3, ph // 2)],
        3: [(pw // 4, ph // 2), (pw // 2, ph // 2), (3 * pw // 4, ph // 2)],
        4: [(pw // 3, ph // 3), (2 * pw // 3, ph // 3),
            (pw // 3, 2 * ph // 3), (2 * pw // 3, 2 * ph // 3)],
    }
    for cx, cy in positions.get(n, []):
        draw_circle(pixels, W, ox + cx, cy, r, FG)
        draw_circle_border(pixels, W, ox + cx, cy, r, WHT, 1)


def build_puzzle1(base):
    panels = [
        lambda p, W, pw, ph, ox: _draw_n_circles(1, p, W, pw, ph, ox),
        lambda p, W, pw, ph, ox: _draw_n_circles(2, p, W, pw, ph, ox),
        lambda p, W, pw, ph, ox: _draw_n_circles(3, p, W, pw, ph, ox),
    ]
    pix, W, H = make_sequence_strip(panels)
    save_png(f"{base}/pattern1.png", pix, W, H)

    option_ns = {"a": 1, "b": 2, "c": 3, "d": 4}
    for opt, n in option_ns.items():
        fn = lambda p, W, pw, ph, ox, _n=n: _draw_n_circles(_n, p, W, pw, ph, ox)
        pix2, w2, h2 = make_option_image(fn)
        save_png(f"{base}/opt_{opt}1.png", pix2, w2, h2)


# ═══════════════════════════════════════════════════════════════════════════════
# PUZZLE 2 — Growing Square
#   Squares grow: 20px → 36px → 52px.  Correct next = 68px.
#   Options: A=20  B=36  C=68 (correct)  D=90 (too big, wrong)
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_square_size(size, pixels, W, pw, ph, ox):
    cx, cy = ox + pw // 2, ph // 2
    x0, y0 = cx - size // 2, cy - size // 2
    fill_rect(pixels, W, x0, y0, x0 + size, y0 + size, HL)
    draw_rect_border(pixels, W, x0, y0, x0 + size, y0 + size, WHT, 2)


def build_puzzle2(base):
    panels = [
        lambda p, W, pw, ph, ox: _draw_square_size(20, p, W, pw, ph, ox),
        lambda p, W, pw, ph, ox: _draw_square_size(36, p, W, pw, ph, ox),
        lambda p, W, pw, ph, ox: _draw_square_size(52, p, W, pw, ph, ox),
    ]
    pix, W, H = make_sequence_strip(panels)
    save_png(f"{base}/pattern2.png", pix, W, H)

    sizes = {"a": 20, "b": 36, "c": 68, "d": 88}
    for opt, s in sizes.items():
        fn = lambda p, W, pw, ph, ox, _s=s: _draw_square_size(_s, p, W, pw, ph, ox)
        pix2, w2, h2 = make_option_image(fn)
        save_png(f"{base}/opt_{opt}2.png", pix2, w2, h2)


# ═══════════════════════════════════════════════════════════════════════════════
# PUZZLE 3 — Filled / Hollow Alternation
#   filled → hollow → filled → ?  Correct = hollow.
#   Options: A=hollow (correct)  B=filled  C=hollow small  D=circle
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_filled_square(pixels, W, pw, ph, ox):
    s = 40
    cx, cy = ox + pw // 2, ph // 2
    fill_rect(pixels, W, cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2, FG)


def _draw_hollow_square(pixels, W, pw, ph, ox):
    s = 40
    cx, cy = ox + pw // 2, ph // 2
    draw_rect_border(pixels, W, cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2, FG, 4)


def _draw_hollow_small(pixels, W, pw, ph, ox):
    s = 24
    cx, cy = ox + pw // 2, ph // 2
    draw_rect_border(pixels, W, cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2, FG, 3)


def _draw_circle_opt(pixels, W, pw, ph, ox):
    cx, cy = ox + pw // 2, ph // 2
    draw_circle_border(pixels, W, cx, cy, 20, FG, 4)


def build_puzzle3(base):
    panels = [_draw_filled_square, _draw_hollow_square, _draw_filled_square]
    pix, W, H = make_sequence_strip(panels)
    save_png(f"{base}/pattern3.png", pix, W, H)

    opts = {"a": _draw_hollow_square, "b": _draw_filled_square,
            "c": _draw_hollow_small, "d": _draw_circle_opt}
    for opt, fn in opts.items():
        pix2, w2, h2 = make_option_image(fn)
        save_png(f"{base}/opt_{opt}3.png", pix2, w2, h2)


# ═══════════════════════════════════════════════════════════════════════════════
# PUZZLE 4 — L-Shape Rotation (90° clockwise each step)
#   0° → 90° → 180° → ?  Correct = 270°.
#   Options: A=0°  B=270° (correct)  C=180°  D=90°
# ═══════════════════════════════════════════════════════════════════════════════

# L-shape is defined as a set of relative (dx, dy) block coords (each block = 10px)
L_SHAPE = [(0,0),(0,1),(0,2),(1,2)]  # long arm going down, foot going right

def _rotate_l(coords, steps):
    """Rotate each coord 90° clockwise `steps` times around origin."""
    result = coords
    for _ in range(steps):
        result = [(cy, -cx) for cx, cy in result]
    # Normalize to positive quadrant
    min_x = min(x for x, y in result)
    min_y = min(y for x, y in result)
    return [(x - min_x, y - min_y) for x, y in result]


def _draw_l_rotation(steps, pixels, W, pw, ph, ox):
    coords = _rotate_l(L_SHAPE, steps)
    block = 14
    pad = 8
    max_x = max(x for x, y in coords)
    max_y = max(y for x, y in coords)
    total_w = (max_x + 1) * block
    total_h = (max_y + 1) * block
    sx = ox + (pw - total_w) // 2
    sy = (ph - total_h) // 2
    for bx, by in coords:
        x0 = sx + bx * block + pad // 2
        y0 = sy + by * block + pad // 2
        fill_rect(pixels, W, x0, y0, x0 + block - pad, y0 + block - pad, GRN)
        draw_rect_border(pixels, W, x0, y0, x0 + block - pad, y0 + block - pad, WHT, 1)


def build_puzzle4(base):
    panels = [
        lambda p, W, pw, ph, ox: _draw_l_rotation(0, p, W, pw, ph, ox),
        lambda p, W, pw, ph, ox: _draw_l_rotation(1, p, W, pw, ph, ox),
        lambda p, W, pw, ph, ox: _draw_l_rotation(2, p, W, pw, ph, ox),
    ]
    pix, W, H = make_sequence_strip(panels)
    save_png(f"{base}/pattern4.png", pix, W, H)

    option_steps = {"a": 0, "b": 3, "c": 2, "d": 1}
    for opt, steps in option_steps.items():
        fn = lambda p, W, pw, ph, ox, _s=steps: _draw_l_rotation(_s, p, W, pw, ph, ox)
        pix2, w2, h2 = make_option_image(fn)
        save_png(f"{base}/opt_{opt}4.png", pix2, w2, h2)


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    base = "static/puzzles"
    print("Generating puzzle images…\n")

    print("Puzzle 1 — Circles Counting (Pattern Recognition)")
    build_puzzle1(base)

    print("\nPuzzle 2 — Growing Square (Spatial Awareness)")
    build_puzzle2(base)

    print("\nPuzzle 3 — Filled/Hollow Alternation (Pattern Recognition)")
    build_puzzle3(base)

    print("\nPuzzle 4 — L-Shape Rotation (Spatial Awareness)")
    build_puzzle4(base)

    print("\n✅ All puzzle images created in static/puzzles/")
