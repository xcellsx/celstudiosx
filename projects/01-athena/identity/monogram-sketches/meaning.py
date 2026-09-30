"""Flourishes with meaning: the mirrored Snell Roundhand A, flourished with one
of Athena's symbols each (olive, owl, spear, helmet crest).

Run: PYTHONPATH=/tmp/pylib python3 meaning.py
"""

import math
import os

from generate import bez, bez_d, chain, leaf, mirror_d, mirror_poly, poly_d, ribbon
from snell import DEEP, GILT, MARBLE, UMBER, apex, label, mirrored_A

HERE = os.path.dirname(os.path.abspath(__file__))
BASE, SCALE = 620, 0.4
APEX_Y = BASE - apex("A")[1] * SCALE


def pair_poly(poly):
    return f'<path d="{poly_d(poly)}"/><path d="{poly_d(mirror_poly(poly))}"/>'


def pair_d(d):
    return f'<path d="{d}"/><path d="{mirror_d(d)}"/>'


def teardrop(base, tip, width, bend=0.0):
    """A closed hairline loop from base out to tip and back, like a feather.
    Positive bend arches the loop upward, negative lets it droop."""
    dx, dy = tip[0] - base[0], tip[1] - base[1]
    length = math.hypot(dx, dy)
    nx, ny = dy / length, -dx / length
    if ny > 0:
        nx, ny = -nx, -ny

    def at(f, w):
        w += bend * math.sin(math.pi * f)
        return (base[0] + dx * f + nx * w, base[1] + dy * f + ny * w)

    return chain(base, (at(0.25, width), at(0.8, width * 0.7), tip), (at(0.85, -width * 0.35), at(0.3, -width * 0.25), base))


def leaves_along(segs, spacing, length, width, spread=38):
    out, side = [], 1
    for s in segs:
        for t in [i / spacing for i in range(1, spacing)]:
            x, y = bez(s, t)
            dx, dy = bez_d(s, t)
            ang = math.degrees(math.atan2(dy, dx)) + side * spread
            out.append(leaf((x, y), ang, length, width))
            side = -side
    return out


def olive():
    stem = chain((500, 835), ((380, 830), (150, 760), (95, 580)), ((60, 450), (110, 320), (215, 235)))
    curl = chain((500, 835), ((524, 848), (562, 850), (566, 826)), ((569, 806), (545, 800), (538, 815)))
    parts = [pair_poly(ribbon(stem, 16, hair=4)), pair_poly(ribbon(curl, 12, hair=4, taper=25))]
    for d in leaves_along(stem, 5, 76, 17):
        parts.append(pair_d(d))
    for cx, cy in ((220, 800), (70, 470)):
        parts.append(f'<ellipse cx="{cx}" cy="{cy}" rx="12" ry="15"/><ellipse cx="{1000 - cx}" cy="{cy}" rx="12" ry="15"/>')
    return "".join(parts)


def owl_wings():
    root = (488, APEX_Y + 24)
    feathers = [((150, 250), 34, -70), ((120, 350), 30, -60), ((150, 450), 26, -50), ((220, 530), 22, -40)]
    return "".join(pair_poly(ribbon(teardrop(root, tip, w, bend), 16, hair=4, taper=30)) for tip, w, bend in feathers)


def spear(width=10, head_len=150):
    shaft = ribbon(chain((500, 250), ((500, 450), (500, 700), (500, 900))), width, hair=width, taper=20, swell=0)
    head = leaf((500, 262), 270, head_len, head_len * 0.22)
    butt = "M500 890 L512 918 L500 950 L488 918 Z"
    bow = ribbon(
        chain((500, 268), ((470, 250), (420, 250), (412, 280)), ((404, 310), (440, 330), (470, 300)), ((485, 285), (492, 272), (500, 268))),
        12,
        hair=4,
        taper=20,
    )
    tail = ribbon(chain((500, 272), ((470, 300), (440, 360), (400, 380))), 12, hair=3, taper=40)
    return f'<path d="{poly_d(shaft)}"/><path d="{head}"/><path d="{butt}"/>' + pair_poly(bow) + pair_poly(tail)


def crest():
    root = (500, APEX_Y + 4)
    parts = [f'<path d="{poly_d(ribbon(teardrop(root, (500, APEX_Y - 240), 30), 16, hair=4, taper=30))}"/>']
    for ang, length, w, bend in ((-118, 250, 28, 60), (-150, 250, 24, 70)):
        a = math.radians(ang)
        tip = (root[0] + length * math.cos(a), root[1] + length * math.sin(a))
        parts.append(pair_poly(ribbon(teardrop(root, tip, w, bend), 16, hair=4, taper=30)))
    return "".join(parts)


def mark(fill, flourish):
    return f'<g fill="{fill}">{mirrored_A(fill, base=BASE, scale=SCALE)}{flourish()}</g>'


def write_sheet():
    p = 800
    body = [f'<rect width="{p * 2}" height="{p * 2}" fill="{UMBER}"/>']
    body.append(f'<rect x="0" y="{p}" width="{p}" height="{p}" fill="{DEEP}"/>')
    panels = [
        (mark(MARBLE, olive), "Olive wreath", "Olive oil: the original ancient beauty secret"),
        (mark(MARBLE, spear), "Spear", "Strength: the goddess, armed"),
        (mark(GILT, owl_wings), "Owl wings", "Wisdom: the owl of Athena spreads its wings"),
        (mark(GILT, lambda: olive() + spear()), "Olive and spear", "Beauty and strength, together"),
    ]
    for i, (art, title, note) in enumerate(panels):
        x0, y0 = (i % 2) * p, (i // 2) * p
        body.append(f'<g transform="translate({x0 + 110} {y0 + 10}) scale(0.58)">{art}</g>')
        body.append(label(x0 + p / 2, y0 + 660, title, note))
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {p * 2} {p * 2}" width="{p * 2}" height="{p * 2}">'
        + "".join(body)
        + "</svg>"
    )
    with open(os.path.join(HERE, "sheet-meaning.svg"), "w") as f:
        f.write(svg)


def small(fill, weight=2):
    """Simplified mark for tiny sizes: heavier Snell weight, spear only."""
    shaft = ribbon(chain((500, 230), ((500, 450), (500, 700), (500, 820))), 16, hair=16, taper=20, swell=0)
    head = leaf((500, 250), 270, 150, 42)
    return (
        f'<g fill="{fill}">{mirrored_A(fill, base=BASE, scale=SCALE, weight=weight)}'
        f'<path d="{poly_d(shaft)}"/><path d="{head}"/></g>'
    )


def coin(fill, weight=2, uid="coin"):
    """Icon for the smallest sizes: the A and spear cropped into a coin."""
    cx, cy, r = 500, 505, 285
    k = 470 / (r + 12)
    shaft = ribbon(chain((500, 330), ((500, 500), (500, 700), (500, 800))), 16, hair=16, taper=1, swell=0)
    head = leaf((500, APEX_Y + 10), 270, 125, 34)
    inner = f'{mirrored_A(fill, base=BASE, scale=SCALE, weight=weight)}<path d="{poly_d(shaft)}"/><path d="{head}"/>'
    return (
        f'<g transform="translate({500 - cx * k} {500 - cy * k}) scale({k})" fill="{fill}">'
        f'<clipPath id="{uid}"><circle cx="{cx}" cy="{cy}" r="{r - 14}"/></clipPath>'
        f'<g clip-path="url(#{uid})">{inner}</g>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{fill}" stroke-width="16"/></g>'
    )


def write_small_sheet():
    w = h = 1000
    body = [f'<rect width="{w}" height="{h}" fill="{UMBER}"/>']
    rows = [
        ("Full mark", lambda f: final(f)),
        ("Small, Black", lambda f: small(f, weight=2)),
        ("Coin icon", None),
    ]
    for r, (name, art) in enumerate(rows):
        if art is None:
            art = lambda f, _r=r: coin(f, uid=f"coin{_r}{len(body)}")
        y = 60 + r * 300
        body.append(
            f'<text x="40" y="{y + 110}" font-family="Didot, serif" font-size="20" letter-spacing="4" fill="{GILT}">{name.upper()}</text>'
        )
        x = 270
        for size in (200, 120, 64, 32, 16):
            s = size / 1000
            body.append(f'<g transform="translate({x} {y + 100 - size / 2}) scale({s})">{art(MARBLE)}</g>')
            body.append(
                f'<text x="{x + size / 2}" y="{y + 210}" text-anchor="middle" font-family="\'Avenir Next\', sans-serif" '
                f'font-size="14" fill="{MARBLE}" opacity="0.6">{size}px</text>'
            )
            x += size + 45
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">' + "".join(body) + "</svg>"
    with open(os.path.join(HERE, "sheet-small.svg"), "w") as f:
        f.write(svg)


def final(fill):
    return mark(fill, lambda: olive() + spear(width=7, head_len=135))


def write_final_sheet():
    p = 800
    body = [f'<rect width="{p * 2}" height="{p * 2}" fill="{UMBER}"/>']
    body.append(f'<rect x="0" y="{p}" width="{p}" height="{p}" fill="{DEEP}"/>')
    body.append(f'<g transform="translate(110 10) scale(0.58)">{final(MARBLE)}</g>')
    body.append(label(p / 2, 660, "Olive and spear", "Marble on umber"))
    body.append(f'<g transform="translate({p + 110} 10) scale(0.58)">{final(GILT)}</g>')
    body.append(label(p + p / 2, 660, "Gold foil", "Gilt on umber, for the compact and box"))
    body.append(f'<g transform="translate(250 {p + 40}) scale(0.3)">{final(GILT)}</g>')
    body.append(
        f'<text x="{p / 2 + 12}" y="{p + 420}" text-anchor="middle" font-family="Didot, serif" '
        f'font-size="64" letter-spacing="24" fill="{MARBLE}">ATHENA</text>'
    )
    body.append(label(p / 2, p + 660, "Lockup", "Mark over the wordmark"))
    x = p + 90
    for size in (240, 120, 64, 32):
        s = size / 1000
        body.append(f'<g transform="translate({x} {p + 330 - size / 2}) scale({s})">{final(MARBLE)}</g>')
        body.append(
            f'<text x="{x + size / 2}" y="{p + 470}" text-anchor="middle" font-family="\'Avenir Next\', sans-serif" '
            f'font-size="16" fill="{MARBLE}" opacity="0.6">{size}px</text>'
        )
        x += size + 40
    body.append(label(p + p / 2, p + 660, "Size test", "Hairlines fade first as it shrinks"))
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {p * 2} {p * 2}" width="{p * 2}" height="{p * 2}">'
        + "".join(body)
        + "</svg>"
    )
    with open(os.path.join(HERE, "sheet-olive-spear.svg"), "w") as f:
        f.write(svg)


if __name__ == "__main__":
    write_sheet()
    write_final_sheet()
    write_small_sheet()
