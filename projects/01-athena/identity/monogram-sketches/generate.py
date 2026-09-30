"""Draws the three Athena monogram sketches as SVG.

Each concept is described as its left half only: cubic Bezier centre lines
on a 1000 x 1000 canvas, centre line at x = 500. Strokes get a pointed-pen
width (thick moving down, hairline moving up) and are mirrored to make the
right half. Run: python3 generate.py
"""

import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
UMBER = "#25190F"
DEEP = "#422F1D"
MARBLE = "#D7D6D5"
GILT = "#C9A45C"


def bez(p, t):
    u = 1 - t
    return (
        u**3 * p[0][0] + 3 * u * u * t * p[1][0] + 3 * u * t * t * p[2][0] + t**3 * p[3][0],
        u**3 * p[0][1] + 3 * u * u * t * p[1][1] + 3 * u * t * t * p[2][1] + t**3 * p[3][1],
    )


def bez_d(p, t):
    u = 1 - t
    return (
        3 * u * u * (p[1][0] - p[0][0]) + 6 * u * t * (p[2][0] - p[1][0]) + 3 * t * t * (p[3][0] - p[2][0]),
        3 * u * u * (p[1][1] - p[0][1]) + 6 * u * t * (p[2][1] - p[1][1]) + 3 * t * t * (p[3][1] - p[2][1]),
    )


def chain(start, *curves):
    """chain((x, y), (c1, c2, end), ...) -> list of cubic segments."""
    segs, cur = [], start
    for c1, c2, end in curves:
        segs.append((cur, c1, c2, end))
        cur = end
    return segs


def smoothstep(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def ribbon(segs, wmax, swell=0.35, hair=3.0, taper=70.0, cap=1.5):
    pts, dirs = [], []
    for s in segs:
        for i in range(60):
            t = i / 60
            pts.append(bez(s, t))
            dirs.append(bez_d(s, t))
    pts.append(bez(segs[-1], 1.0))
    dirs.append(bez_d(segs[-1], 1.0))

    lengths = [0.0]
    for a, b in zip(pts, pts[1:]):
        lengths.append(lengths[-1] + math.dist(a, b))
    total = lengths[-1]

    widths = []
    for (dx, dy), s in zip(dirs, lengths):
        n = math.hypot(dx, dy) or 1.0
        down = max(0.0, dy / n) ** 0.8
        w = hair + (wmax - hair) * down * ((1 - swell) + swell * math.sin(math.pi * s / total))
        end = smoothstep(min(s, total - s) / taper)
        widths.append(cap + (w - cap) * end)
    k = 6
    widths = [
        sum(widths[max(0, i - k) : i + k + 1]) / len(widths[max(0, i - k) : i + k + 1])
        for i in range(len(widths))
    ]

    left, right = [], []
    for (x, y), (dx, dy), w in zip(pts, dirs, widths):
        n = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / n, dx / n
        left.append((x + nx * w / 2, y + ny * w / 2))
        right.append((x - nx * w / 2, y - ny * w / 2))
    return left + right[::-1]


def leaf(base, angle_deg, length, width):
    a = math.radians(angle_deg)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    bx, by = base
    tip = (bx + ux * length, by + uy * length)
    mid = (bx + ux * length * 0.45, by + uy * length * 0.45)
    c1 = (mid[0] + nx * width, mid[1] + ny * width)
    c2 = (mid[0] - nx * width, mid[1] - ny * width)
    return f"M{bx:.1f} {by:.1f} Q{c1[0]:.1f} {c1[1]:.1f} {tip[0]:.1f} {tip[1]:.1f} Q{c2[0]:.1f} {c2[1]:.1f} {bx:.1f} {by:.1f} Z"


def poly_d(poly):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in poly) + " Z"


def mirror_poly(poly):
    return [(1000 - x, y) for x, y in poly]


def mirror_d(d):
    out, tokens = [], d.replace("M", " M ").replace("Q", " Q ").replace("Z", " Z ").split()
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok in ("M", "Q", "Z"):
            out.append(tok)
            i += 1
        else:
            out.append(f"{1000 - float(tok):.1f} {tokens[i + 1]}")
            i += 2
    return " ".join(out)


# --- Concept 1: hidden owl -------------------------------------------------
# The A's legs cross at the apex into two ear tufts, the crossbar is two
# looping eyes, and the eye strokes cross below them where a small beak sits.
OWL = {
    "strokes": [
        (
            chain(
                (555, 165),
                ((535, 185), (515, 210), (500, 245)),
                ((440, 330), (300, 640), (245, 835)),
                ((230, 870), (180, 865), (175, 830)),
                ((172, 808), (190, 795), (207, 805)),
            ),
            32,
        ),
        (
            chain(
                (540, 600),
                ((515, 570), (497, 530), (496, 470)),
                ((496, 446), (476, 426), (452, 426)),
                ((428, 426), (408, 446), (408, 470)),
                ((408, 494), (428, 514), (452, 514)),
                ((472, 514), (484, 503), (487, 490)),
            ),
            30,
            5,
        ),
    ],
    "shapes": ["M500 532 Q515 552 500 588 Q485 552 500 532 Z"],
    "mirror_shapes": [],
}

# --- Concept 2: helmet -----------------------------------------------------
# A pointed helmet dome forms the A, the crest fans out above the apex, the
# eye slits are the crossbar, and the cheek guards leave the T opening below.
HELMET = {
    "strokes": [
        (
            chain(
                (500, 270),
                ((430, 330), (320, 420), (315, 560)),
                ((312, 690), (380, 790), (445, 835)),
            ),
            30,
        ),
        (
            chain(
                (488, 522),
                ((445, 488), (380, 480), (335, 505)),
                ((380, 540), (445, 545), (488, 526)),
            ),
            14,
            5,
        ),
        (chain((500, 440), ((500, 500), (500, 560), (500, 610))), 22),
        (
            chain(
                (500, 70),
                ((440, 120), (410, 190), (445, 235)),
                ((465, 258), (488, 266), (500, 272)),
            ),
            26,
        ),
        (chain((500, 150), ((500, 190), (500, 235), (500, 272))), 16),
    ],
    "shapes": [],
    "mirror_shapes": [],
}

# --- Concept 3: olive flourish -----------------------------------------------
# A plain calligraphic A: the crossbar is a cupid's-bow swash (a nod to lips),
# the feet sweep out into olive sprigs, and two small leaves crown the apex.
OLIVE = {
    "strokes": [
        (
            chain(
                (500, 215),
                ((470, 320), (385, 600), (335, 800)),
                ((318, 868), (255, 888), (212, 860)),
                ((188, 844), (192, 808), (222, 802)),
            ),
            40,
        ),
        (chain((385, 560), ((428, 612), (476, 612), (500, 578))), 16, 7),
    ],
    "shapes": [],
    "mirror_shapes": [
        leaf((300, 872), 115, 80, 18),
        leaf((250, 884), 150, 72, 16),
        leaf((494, 205), 235, 78, 17),
        leaf((490, 228), 195, 62, 14),
        ("circle", 272, 922, 14),
    ],
}

CONCEPTS = [
    ("owl", "Hidden owl", "The loops are the owl's eyes", OWL),
    ("helmet", "Helmet", "Plume crest, almond eyes, cheek guards", HELMET),
    ("olive", "Olive flourish", "Olive sprigs and a cupid's-bow crossbar", OLIVE),
]


def monogram_paths(concept, fill):
    parts = []
    for segs, wmax, *hair in concept["strokes"]:
        poly = ribbon(segs, wmax, hair=hair[0] if hair else 3.0)
        parts.append(f'<path d="{poly_d(poly)}"/>')
        parts.append(f'<path d="{poly_d(mirror_poly(poly))}"/>')
    for d in concept["mirror_shapes"]:
        if isinstance(d, tuple):
            _, cx, cy, r = d
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}"/>')
            parts.append(f'<circle cx="{1000 - cx}" cy="{cy}" r="{r}"/>')
            continue
        parts.append(f'<path d="{d}"/>')
        parts.append(f'<path d="{mirror_d(d)}"/>')
    for d in concept["shapes"]:
        parts.append(f'<path d="{d}"/>')
    return f'<g fill="{fill}" fill-rule="nonzero">' + "".join(parts) + "</g>"


def write_single(slug, concept):
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="1000" height="1000">'
        f'<rect id="background" width="1000" height="1000" fill="{UMBER}"/>'
        f"{monogram_paths(concept, MARBLE)}</svg>"
    )
    with open(os.path.join(HERE, f"{slug}.svg"), "w") as f:
        f.write(svg)


def label(cx, y, title, note):
    return (
        f'<text x="{cx + 4}" y="{y}" text-anchor="middle" font-family="Didot, \'Bodoni 72\', serif" '
        f'font-size="26" letter-spacing="8" fill="{GILT}">{title.upper()}</text>'
        f'<text x="{cx}" y="{y + 38}" text-anchor="middle" font-family="\'Avenir Next\', sans-serif" '
        f'font-size="18" fill="{MARBLE}" opacity="0.7">{note}</text>'
    )


def write_sheet():
    panel = 800
    body = [f'<rect width="{panel * 2}" height="{panel * 2}" fill="{UMBER}"/>']
    body.append(f'<line x1="{panel}" x2="{panel}" y1="60" y2="{panel * 2 - 60}" stroke="{DEEP}" stroke-width="2"/>')
    body.append(f'<line x1="60" x2="{panel * 2 - 60}" y1="{panel}" y2="{panel}" stroke="{DEEP}" stroke-width="2"/>')
    for i, (_, title, note, concept) in enumerate(CONCEPTS):
        x0, y0 = (i % 2) * panel, (i // 2) * panel
        body.append(f'<g transform="translate({x0 + 150} {y0 + 70}) scale(0.5)">')
        body.append(monogram_paths(concept, MARBLE))
        body.append("</g>")
        body.append(label(x0 + panel / 2, y0 + 640, title, note))
    x0 = y0 = panel
    body.append(
        f'<text x="{x0 + 400 + 14}" y="{y0 + 420}" text-anchor="middle" font-family="Didot, \'Bodoni 72\', serif" '
        f'font-size="96" letter-spacing="28" fill="{MARBLE}">ATHENA</text>'
    )
    body.append(label(x0 + 400, y0 + 640, "Wordmark", "Didone capitals, letterspaced (Bodoni Moda later)"))
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {panel * 2} {panel * 2}" '
        f'width="{panel * 2}" height="{panel * 2}">' + "".join(body) + "</svg>"
    )
    with open(os.path.join(HERE, "sheet.svg"), "w") as f:
        f.write(svg)


if __name__ == "__main__":
    for slug, _, _, concept in CONCEPTS:
        write_single(slug, concept)
    write_sheet()
