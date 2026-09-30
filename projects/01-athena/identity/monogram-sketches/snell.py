"""A + a monogram studies from Snell Roundhand outlines (macOS system font).

Needs fontTools: python3 -m pip install --target /tmp/pylib fonttools
Run: PYTHONPATH=/tmp/pylib python3 snell.py
"""

import os

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTCollection

from generate import chain, mirror_poly, poly_d, ribbon, spiral

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = "/System/Library/Fonts/Supplemental/SnellRoundhand.ttc"
UMBER = "#25190F"
DEEP = "#422F1D"
MARBLE = "#D7D6D5"
GILT = "#C9A45C"

_fonts = TTCollection(FONT_PATH).fonts


def _glyph(ch, weight):
    font = _fonts[weight]
    gs = font.getGlyphSet()
    return gs, gs[font.getBestCmap()[ord(ch)]]


def bounds(ch, weight=0):
    gs, g = _glyph(ch, weight)
    pen = BoundsPen(gs)
    g.draw(pen)
    return pen.bounds


def path(ch, x, y, scale, mirror=False, weight=0):
    """Glyph outline as an SVG path. (x, y) is where the glyph origin (left
    edge of the advance, on the baseline) lands; mirror flips around x."""
    gs, g = _glyph(ch, weight)
    pen = SVGPathPen(gs)
    sx = -scale if mirror else scale
    g.draw(TransformPen(pen, (sx, 0, 0, -scale, x, y)))
    return pen.getCommands()


def apex(ch="A", weight=0):
    from fontTools.pens.recordingPen import RecordingPen

    gs, g = _glyph(ch, weight)
    pen = RecordingPen()
    g.draw(pen)
    pts = [p for _, args in pen.value for p in args if p]
    return max(pts, key=lambda p: p[1])


def mirrored_A(fill, cx=500, base=700, scale=0.42, overlap=0, weight=0):
    """Two Snell A's flipped around the apex so the thick legs form one A."""
    ax = apex("A", weight)[0]
    x = cx - (ax - overlap) * scale
    return (
        f'<path d="{path("A", x, base, scale, weight=weight)}" fill="{fill}"/>'
        f'<path d="{path("A", 2 * cx - x, base, scale, mirror=True, weight=weight)}" fill="{fill}"/>'
    )


def mirrored_a(fill, cx=500, base=700, scale=0.42, gap=0, weight=0, pupils=False):
    parts = [
        f'<path d="{path("a", cx + gap, base, scale, weight=weight)}" fill="{fill}"/>',
        f'<path d="{path("a", cx - gap, base, scale, mirror=True, weight=weight)}" fill="{fill}"/>',
    ]
    if pupils:
        for s in (-1, 1):
            parts.append(
                f'<circle cx="{cx + s * (gap + 170 * scale):.1f}" cy="{base - 170 * scale:.1f}" r="{30 * scale:.1f}" fill="{fill}"/>'
            )
    return "".join(parts)


def typed_Aa(fill, x=120, base=700, scale=0.42):
    font = _fonts[0]
    adv = font["hmtx"][font.getBestCmap()[ord("A")]][0]
    return f'<path d="{path("A", x, base, scale)}" fill="{fill}"/><path d="{path("a", x + adv * scale, base, scale)}" fill="{fill}"/>'


def label(cx, y, title, note):
    return (
        f'<text x="{cx + 4}" y="{y}" text-anchor="middle" font-family="Didot, serif" '
        f'font-size="26" letter-spacing="8" fill="{GILT}">{title.upper()}</text>'
        f'<text x="{cx}" y="{y + 38}" text-anchor="middle" font-family="\'Avenir Next\', sans-serif" '
        f'font-size="18" fill="{MARBLE}" opacity="0.7">{note}</text>'
    )


def write_sheet(panels, name):
    p = 800
    body = [f'<rect width="{p * 2}" height="{p * 2}" fill="{UMBER}"/>']
    body.append(f'<rect x="0" y="{p}" width="{p}" height="{p}" fill="{DEEP}"/>')
    for i, (art, title, note) in enumerate(panels):
        x0, y0 = (i % 2) * p, (i // 2) * p
        body.append(f'<g transform="translate({x0 + 40} {y0 + 20}) scale(0.72)">{art}</g>')
        body.append(label(x0 + p / 2, y0 + 660, title, note))
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {p * 2} {p * 2}" width="{p * 2}" height="{p * 2}">'
        + "".join(body)
        + "</svg>"
    )
    with open(os.path.join(HERE, name), "w") as f:
        f.write(svg)


def write_probe():
    parts = [f'<rect width="1000" height="600" fill="{UMBER}"/>']
    for i, ch in enumerate("Aa"):
        b = bounds(ch)
        x = 60 + i * 480
        parts.append(f'<path d="{path(ch, x, 450, 0.4)}" fill="{MARBLE}"/>')
        parts.append(
            f'<line x1="{x}" y1="40" x2="{x}" y2="560" stroke="{GILT}" stroke-width="1"/>'
            f'<text x="{x + 5}" y="590" font-size="18" fill="{GILT}" font-family="Avenir Next">{ch} bounds {b}</text>'
        )
    with open("/tmp/snell-probe.svg", "w") as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 600" width="1000" height="600">' + "".join(parts) + "</svg>")


def pair(poly):
    return f'<path d="{poly_d(poly)}"/><path d="{poly_d(mirror_poly(poly))}"/>'


def heart_crown(apex_y, k=0.85):
    """Two hairline lobes rising from the apex into a small heart."""
    def pt(dx, dy):
        return (500 + dx * k, apex_y + dy * k)

    return pair(
        ribbon(
            chain(
                pt(0, 0),
                (pt(-30, -22), pt(-82, -58), pt(-76, -92)),
                (pt(-70, -124), pt(-18, -124), pt(0, -82)),
            ),
            14,
            hair=5,
            taper=30,
        )
    )


def heart_frame():
    """A large heart round the mark; the strokes cross at the point and curl."""
    return pair(
        ribbon(
            chain(
                (500, 200),
                ((470, 120), (380, 68), (290, 74)),
                ((150, 84), (40, 212), (58, 400)),
                ((78, 600), (300, 750), (500, 885)),
                ((524, 902), (574, 906), (582, 876)),
            )
            + spiral((556, 866), 27, 6, 20, -400),
            18,
            hair=5,
        )
    )


def flourished(fill, crown=True, frame=True, smalls=False, pupils=False):
    base, scale = 590, 0.38
    if not frame:
        base, scale = 690, 0.42
    apex_y = base - apex("A")[1] * scale
    parts = [mirrored_A(fill, base=base, scale=scale)]
    if crown:
        parts.append(heart_crown(apex_y))
    if frame:
        parts.append(heart_frame())
    if smalls:
        parts.append(mirrored_a(fill, base=790, scale=0.32, gap=3, pupils=pupils))
    return f'<g fill="{fill}">' + "".join(parts) + "</g>"


def write_heart_sheet():
    p = 800
    body = [f'<rect width="{p * 2}" height="{p * 2}" fill="{UMBER}"/>']
    body.append(f'<rect x="0" y="{p}" width="{p}" height="{p}" fill="{DEEP}"/>')
    panels = [
        (flourished(MARBLE, frame=False), "Heart crown", "Two lobes rise from the apex"),
        (flourished(MARBLE), "Heart frame", "Crossed and curled at the point"),
        (flourished(GILT, smalls=True), "Aa in a heart", "Mirrored a's fill the lower heart"),
        (flourished(GILT, smalls=True, pupils=True), "Owl in a heart", "Pupils make the a's into eyes"),
    ]
    for i, (art, title, note) in enumerate(panels):
        x0, y0 = (i % 2) * p, (i // 2) * p
        body.append(f'<g transform="translate({x0 + 110} {y0 + 20}) scale(0.58)">{art}</g>')
        body.append(label(x0 + p / 2, y0 + 660, title, note))
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {p * 2} {p * 2}" width="{p * 2}" height="{p * 2}">'
        + "".join(body)
        + "</svg>"
    )
    with open(os.path.join(HERE, "sheet-snell-hearts.svg"), "w") as f:
        f.write(svg)


def combos():
    write_sheet(
        [
            (mirrored_A(MARBLE, base=640) + mirrored_a(MARBLE, base=640, scale=0.22, gap=2), "a in the heart", "Small a's inside the mirrored A"),
            (mirrored_A(MARBLE, base=560) + mirrored_a(MARBLE, base=800, scale=0.45, gap=4), "A over a", "Mirrored A stacked on mirrored a's"),
            (mirrored_A(GILT, base=560) + mirrored_a(GILT, base=722, scale=0.45, gap=4, pupils=True), "Owl", "The A arch is the brow, the a's the eyes"),
            (mirrored_A(GILT, base=620, overlap=60) + mirrored_a(GILT, base=700, scale=0.36, gap=4), "Interlaced", "a's overlap the A's legs"),
        ],
        "sheet-snell-combo.svg",
    )


if __name__ == "__main__":
    write_heart_sheet()
    combos()
    write_sheet(
        [
            (typed_Aa(MARBLE), "As typed", "Snell Roundhand A and a"),
            (mirrored_A(MARBLE), "Mirrored A", "Flipped around the apex"),
            (mirrored_A(MARBLE, overlap=60), "Crossed A", "Legs cross at the apex"),
            (mirrored_a(MARBLE, scale=0.6, base=620), "Mirrored a", "Bowls back to back"),
        ],
        "sheet-snell-probe.svg",
    )
