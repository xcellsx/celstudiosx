"""Owl-face monogram studies built from mirrored italic "a" glyphs.

Uses the system Didot Italic as a stand-in for the Affinity font.
Run: python3 owl-letters.py
"""

import math
import os

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
                f'<circle cx="{cx + s * (gap + size * 0.125):.1f}" cy="{cy - size * 0.195:.1f}" '
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


if __name__ == "__main__":
    write_sheet()
