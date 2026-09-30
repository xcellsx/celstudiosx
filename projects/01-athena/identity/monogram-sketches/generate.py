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


def spiral(center, r0, r1, a0, sweep, step=30):
    """Spiral as cubic segments. Angles in degrees, SVG orientation (y down):
    positive sweep turns clockwise on screen. Radius eases from r0 to r1."""
    cx, cy = center
    n = max(1, math.ceil(abs(sweep) / step))
    d_theta = math.radians(sweep) / n
    dr = (r1 - r0) / n

    def point(i):
        th = math.radians(a0) + d_theta * i
        r = r0 + dr * i
        p = (cx + r * math.cos(th), cy + r * math.sin(th))
        v = (
            (dr / d_theta) * math.cos(th) - r * math.sin(th),
            (dr / d_theta) * math.sin(th) + r * math.cos(th),
        )
        return p, v

    segs = []
    for i in range(n):
        (p0, v0), (p3, v3) = point(i), point(i + 1)
        k = d_theta / 3
        segs.append((p0, (p0[0] + v0[0] * k, p0[1] + v0[1] * k), (p3[0] - v3[0] * k, p3[1] - v3[1] * k), p3))
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

# --- Concept 3b: olive scrolls ------------------------------------------------
# The legs cross at the apex and roll into Ionic-capital volutes, the feet wind
# into spirals that sprout olive leaves, and the cupid's-bow crossbar ends in
# small curls outside the legs.
OLIVE_SCROLL = {
    "strokes": [
        (
            spiral((598, 212), 9, 50, 810, -540)
            + chain(
                (598, 162),
                ((560, 162), (512, 200), (500, 240)),
                ((472, 336), (335, 660), (335, 815)),
            )
            + spiral((275, 815), 60, 12, 0, 480),
            36,
        ),
        (
            chain((500, 580), ((478, 622), (385, 632), (322, 632)))
            + spiral((322, 604), 28, 6, 90, 450),
            16,
            4,
        ),
    ],
    "shapes": [leaf((500, 196), 270, 64, 13)],
    "mirror_shapes": [
        leaf((252, 856), 118, 78, 17),
        leaf((238, 842), 158, 70, 15),
    ],
}

# --- Concept 4: flourished A ---------------------------------------------------
# Copperplate-style flourishing: only the legs carry heavy shades; the loops are
# hairline ovals with light swells, crossing the letter at near right angles.
def flourish(step=30):
    return {
    "strokes": [
        # leg, running on into the start of the foot swash
        (chain((500, 240), ((470, 340), (380, 620), (330, 800)), ((314, 862), (250, 900), (180, 878))), 38),
        # crown: rises past the apex, loops over the top and curls in
        (
            chain(
                (500, 240),
                ((525, 180), (560, 110), (520, 75)),
                ((480, 42), (385, 55), (375, 120)),
                ((366, 180), (430, 215), (462, 190)),
            )
            + spiral((440, 175), 27, 6, 34, -420, step),
            18,
            3,
        ),
        # foot: big oval swash under the leg, back up and into a spiral
        (
            chain(
                (330, 800),
                ((314, 862), (250, 900), (180, 878)),
                ((105, 855), (95, 755), (160, 722)),
                ((225, 690), (300, 735), (282, 785)),
            )
            + spiral((245, 772), 39, 8, 20, 420, step),
            20,
            3,
        ),
        # crossbar: hairline from the centre, crosses the leg, loops outside it
        (
            chain(
                (500, 575),
                ((455, 548), (365, 535), (300, 565)),
                ((235, 596), (245, 670), (305, 660)),
                ((355, 652), (372, 606), (345, 590)),
            ),
            14,
            3,
        ),
        # long outer swash from the crown loop down past the crossbar loop
        (
            chain(
                (375, 120),
                ((330, 200), (200, 300), (180, 450)),
                ((165, 560), (215, 610), (250, 600)),
            ),
            16,
            3,
        ),
    ],
    "shapes": [leaf((500, 232), 270, 56, 12)],
    "mirror_shapes": [],
    }


FLOURISH = flourish()

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


def write_olive_sheet():
    panel = 800
    body = [f'<rect width="{panel * 2}" height="{panel * 2}" fill="{UMBER}"/>']
    body.append(f'<rect x="0" y="{panel}" width="{panel}" height="{panel}" fill="{DEEP}"/>')
    body.append(f'<line x1="{panel}" x2="{panel}" y1="60" y2="{panel - 60}" stroke="{DEEP}" stroke-width="2"/>')
    panels = [
        (0, 0, OLIVE, MARBLE, "Before", "Olive flourish, first sketch"),
        (panel, 0, OLIVE_SCROLL, MARBLE, "Olive scrolls", "Ionic volutes, spiral feet, curled crossbar"),
        (0, panel, OLIVE_SCROLL, GILT, "Gold foil", "Gilt on deep umber, as on a compact lid"),
    ]
    for x0, y0, concept, fill, title, note in panels:
        body.append(f'<g transform="translate({x0 + 150} {y0 + 70}) scale(0.5)">')
        body.append(monogram_paths(concept, fill))
        body.append("</g>")
        body.append(label(x0 + panel / 2, y0 + 640, title, note))
    x0 = y0 = panel
    body.append(f'<g transform="translate({x0 + 290} {y0 + 90}) scale(0.22)">')
    body.append(monogram_paths(OLIVE_SCROLL, GILT))
    body.append("</g>")
    body.append(
        f'<text x="{x0 + 400 + 12}" y="{y0 + 410}" text-anchor="middle" font-family="Didot, \'Bodoni 72\', serif" '
        f'font-size="80" letter-spacing="24" fill="{MARBLE}">ATHENA</text>'
    )
    body.append(label(x0 + 400, y0 + 640, "Lockup", "Monogram over the wordmark"))
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {panel * 2} {panel * 2}" '
        f'width="{panel * 2}" height="{panel * 2}">' + "".join(body) + "</svg>"
    )
    with open(os.path.join(HERE, "sheet-olive.svg"), "w") as f:
        f.write(svg)


if __name__ == "__main__":
    for slug, _, _, concept in CONCEPTS:
        write_single(slug, concept)
    write_single("olive-scroll", OLIVE_SCROLL)
    write_single("flourish", FLOURISH)
    write_sheet()
    write_olive_sheet()
