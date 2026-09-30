"""Flourished capital A combined with italic lowercase a's.

Uses the system Didot Italic for the a's as a stand-in.
Run: python3 combo.py
"""

import os

from generate import DEEP, GILT, MARBLE, UMBER, flourish, monogram_paths

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = "Didot, 'Bodoni 72', serif"


def glyph(x, y, size, fill, mirror=False, anchor="start"):
    t = f"translate({x} {y})" + (" scale(-1 1)" if mirror else "")
    return (
        f'<text transform="{t}" text-anchor="{anchor}" font-family="{FONT}" font-style="italic" '
        f'font-size="{size}" fill="{fill}">a</text>'
    )


def capital(fill, crossbar=True):
    concept = flourish()
    if not crossbar:
        concept["strokes"] = [s for i, s in enumerate(concept["strokes"]) if i != 3]
    return monogram_paths(concept, fill)


def single_a(fill):
    return capital(fill, crossbar=False) + glyph(500, 720, 300, fill, anchor="middle")


def paired_a(fill, gap=4, size=250, base=748, pupils=False):
    parts = [capital(fill), glyph(500 - gap, base, size, fill, mirror=True), glyph(500 + gap, base, size, fill)]
    if pupils:
        for s in (-1, 1):
            parts.append(f'<circle cx="{500 + s * (gap + size * 0.175):.1f}" cy="{base - size * 0.2:.1f}" r="{size * 0.04:.1f}" fill="{fill}"/>')
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
    panels = [
        (0, 0, single_a(MARBLE), "One a", "An italic a sits in as the crossbar"),
        (p, 0, paired_a(MARBLE), "Mirrored a's", "Two a's back to back under the crossbar"),
        (0, p, paired_a(GILT, pupils=True), "Hidden owl", "Pupils turn the a's into owl eyes"),
        (p, p, paired_a(GILT), "Gold foil", "Mirrored a's, gilt on umber"),
    ]
    for x0, y0, art, title, note in panels:
        body.append(f'<g transform="translate({x0 + 130} {y0 + 40}) scale(0.54)">{art}</g>')
        body.append(label(x0 + p / 2, y0 + 660, title, note))
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {p * 2} {p * 2}" width="{p * 2}" height="{p * 2}">'
        + "".join(body)
        + "</svg>"
    )
    with open(os.path.join(HERE, "sheet-combo.svg"), "w") as f:
        f.write(svg)


if __name__ == "__main__":
    write_sheet()
