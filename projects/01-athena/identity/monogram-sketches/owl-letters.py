"""Owl-face monogram studies built from mirrored italic "a" glyphs.

Uses the system Didot Italic as a stand-in for the Affinity font.
Run: python3 owl-letters.py
"""

import math
import os

from generate import chain, mirror_poly, poly_d, ribbon

HERE = os.path.dirname(os.path.abspath(__file__))
UMBER = "#25190F"
DEEP = "#422F1D"
MARBLE = "#D7D6D5"
GILT = "#C9A45C"
FONT = "Didot, 'Bodoni 72', serif"


def glyph(ch, x, y, size, fill, mirror=False, extra=""):
    t = f"translate({x} {y})" + (" scale(-1 1)" if mirror else "")
    return (
        f'<text transform="{t}" font-family="{FONT}" font-style="italic" font-size="{size}" '
        f'fill="{fill}" {extra}>{ch}</text>'
    )


def owl(cx, cy, size, fill, gap, beak_dy, beak_size, pupils=False, ring=False):
    parts = [
        glyph("a", cx - gap, cy, size, fill, mirror=True),
        glyph("a", cx + gap, cy, size, fill),
        glyph("v", cx - beak_size * 0.23, cy + beak_dy, beak_size, fill),
    ]
    if pupils:
        for s in (-1, 1):
            parts.append(
                f'<circle cx="{cx + s * (gap + size * 0.175):.1f}" cy="{cy - size * 0.2:.1f}" '
                f'r="{size * 0.035:.1f}" fill="{fill}"/>'
            )
    if ring:
        r = size * 0.62
        for i in range(48):
            a = 2 * math.pi * i / 48
            parts.append(
                f'<circle cx="{cx + r * math.cos(a):.1f}" cy="{cy - size * 0.2 + r * math.sin(a):.1f}" '
                f'r="{size * 0.012:.1f}" fill="{fill}"/>'
            )
    return "".join(parts)


def label(cx, y, title, note):
    return (
        f'<text x="{cx + 4}" y="{y}" text-anchor="middle" font-family="{FONT}" '
        f'font-size="26" letter-spacing="8" fill="{GILT}">{title.upper()}</text>'
        f'<text x="{cx}" y="{y + 38}" text-anchor="middle" font-family="\'Avenir Next\', sans-serif" '
        f'font-size="18" fill="{MARBLE}" opacity="0.7">{note}</text>'
    )


def write_sheet():
    p = 800
    body = [f'<rect width="{p * 2}" height="{p * 2}" fill="{UMBER}"/>']
    body.append(f'<rect x="0" y="{p}" width="{p}" height="{p}" fill="{DEEP}"/>')
    body.append(owl(400, 420, 420, MARBLE, 0, 150, 200))
    body.append(label(400, 640, "As drawn", "Two mirrored a's, v below"))
    body.append(owl(p + 400, 420, 420, MARBLE, 14, 40, 150))
    body.append(label(p + 400, 640, "Beak tucked in", "Eyes spaced apart, v between them"))
    body.append(owl(400, p + 440, 420, GILT, 14, 40, 150, pupils=True))
    body.append(label(400, p + 640, "Pupils", "A dot in each bowl makes the eyes"))
    body.append(owl(p + 400, p + 450, 360, GILT, 12, 34, 128, pupils=True, ring=True))
    body.append(label(p + 400, p + 640, "Coin", "Beaded rim, like an owl drachm"))
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {p * 2} {p * 2}" width="{p * 2}" height="{p * 2}">'
        + "".join(body)
        + "</svg>"
    )
    with open(os.path.join(HERE, "sheet-owl-letters.svg"), "w") as f:
        f.write(svg)


def owl_brows(fill, gap=70, size=380, base=660, brows=True, pupils=True, ring=False, disc=False):
    """Owl face on a 1000 x 1000 box: mirrored a's for eyes, and the little
    owl's V brows sweeping down into the beak (replacing the letter v)."""
    parts = [
        glyph("a", 500 - gap, base, size, fill, mirror=True),
        glyph("a", 500 + gap, base, size, fill),
    ]
    if pupils:
        for s in (-1, 1):
            parts.append(
                f'<circle cx="{500 + s * (gap + size * 0.175):.1f}" cy="{base - size * 0.2:.1f}" '
                f'r="{size * 0.035:.1f}" fill="{fill}"/>'
            )
    if brows:
        brow = ribbon(
            chain(
                (300, 420),
                ((336, 440), (376, 452), (414, 454)),
                ((466, 458), (496, 530), (500, 640)),
            ),
            30,
            hair=4,
            taper=50,
        )
        parts.append(f'<path d="{poly_d(brow)}"/><path d="{poly_d(mirror_poly(brow))}"/>')
    else:
        parts.append(glyph("v", 500 - 150 * 0.23, base + 40, 150, fill))
    if disc:
        rim = ribbon(chain((300, 420), ((170, 470), (150, 700), (320, 790)), ((400, 830), (470, 840), (500, 850))), 22, hair=3)
        parts.append(f'<path d="{poly_d(rim)}"/><path d="{poly_d(mirror_poly(rim))}"/>')
    if ring:
        for i in range(56):
            a = 2 * math.pi * i / 56
            parts.append(
                f'<circle cx="{500 + 400 * math.cos(a):.1f}" cy="{540 + 400 * math.sin(a):.1f}" r="6" fill="{fill}"/>'
            )
    return f'<g fill="{fill}">' + "".join(parts) + "</g>"


def write_brow_sheet():
    p = 800
    body = [f'<rect width="{p * 2}" height="{p * 2}" fill="{UMBER}"/>']
    body.append(f'<rect x="0" y="{p}" width="{p}" height="{p}" fill="{DEEP}"/>')
    panels = [
        (0, 0, MARBLE, dict(gap=14, brows=False), "Eyes only", "Reads as a face, not yet an owl"),
        (p, 0, MARBLE, {}, "V brows", "The little owl's stern brows become the beak"),
        (0, p, GILT, dict(disc=True), "Facial disc", "A heart-shaped rim frames the face"),
        (p, p, GILT, dict(disc=True, ring=True), "Coin", "Beaded rim, like an owl drachm"),
    ]
    for x0, y0, fill, opts, title, note in panels:
        body.append(f'<g transform="translate({x0 + 100} {y0 - 36}) scale(0.6)">{owl_brows(fill, **opts)}</g>')
        body.append(label(x0 + p / 2, y0 + 640, title, note))
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {p * 2} {p * 2}" width="{p * 2}" height="{p * 2}">'
        + "".join(body)
        + "</svg>"
    )
    with open(os.path.join(HERE, "sheet-owl-brows.svg"), "w") as f:
        f.write(svg)


if __name__ == "__main__":
    write_sheet()
    write_brow_sheet()
