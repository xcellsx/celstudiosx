"""Tracing templates for the flourished A, for placing into Affinity.

Each SVG has named groups (Affinity shows them as layers): guides, a faint
filled shape for both halves, and the left-half Pen path with its nodes and
handles. Spirals use quarter-turn nodes, the way you'd click them with the Pen.
Run: python3 template.py
"""

import math
import os

from generate import FLOURISH, chain, flourish, leaf, mirror_d, mirror_poly, poly_d, ribbon, spiral

HERE = os.path.dirname(os.path.abspath(__file__))
INK = "#25190F"
ROSE = "#A8474A"
BRONZE = "#62503C"

PLAIN = {
    "strokes": [
        (chain((500, 200), ((470, 320), (385, 620), (340, 800)), ((330, 845), (300, 862), (268, 850))), 36),
        (chain((372, 610), ((420, 598), (470, 596), (500, 600))), 14, 5),
    ],
    "leaves": [],
}

SCROLLS = {
    "strokes": [
        (
            spiral((598, 212), 9, 50, 810, -540, step=90)
            + chain((598, 162), ((560, 162), (512, 200), (500, 240)), ((472, 336), (335, 660), (335, 815)))
            + spiral((275, 815), 60, 12, 0, 450, step=90),
            36,
        ),
        (chain((500, 580), ((478, 622), (385, 632), (322, 632))) + spiral((322, 604), 28, 6, 90, 450, step=90), 16, 4),
    ],
    "leaves": [leaf((252, 856), 118, 78, 17), leaf((238, 842), 158, 70, 15)],
    "centre_leaf": leaf((500, 196), 270, 64, 13),
}


def label_offset(node, nodes, dist=16):
    near = [n for n in nodes if n is not node and math.dist(n, node) < 90]
    if not near:
        return 9, -9
    cx = sum(n[0] for n in near) / len(near)
    cy = sum(n[1] for n in near) / len(near)
    dx, dy = node[0] - cx, node[1] - cy
    length = math.hypot(dx, dy) or 1.0
    return dx / length * dist - 5, dy / length * dist + 5


def skeleton(segs, prefix):
    d = f"M{segs[0][0][0]:.1f} {segs[0][0][1]:.1f}" + "".join(
        f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p[0]:.1f} {p[1]:.1f}" for _, c1, c2, p in segs
    )
    out = [f'<path d="{d}" fill="none" stroke="{ROSE}" stroke-width="2"/>']
    for p0, c1, c2, p3 in segs:
        for a, b in ((p0, c1), (p3, c2)):
            out.append(
                f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{BRONZE}" stroke-width="1"/>'
                f'<circle cx="{b[0]:.1f}" cy="{b[1]:.1f}" r="4" fill="#fff" stroke="{BRONZE}" stroke-width="1"/>'
            )
    nodes = [segs[0][0]] + [s[3] for s in segs]
    for i, node in enumerate(nodes, 1):
        x, y = node
        ox, oy = label_offset(node, nodes)
        out.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{ROSE}"/>'
            f'<text x="{x + ox:.1f}" y="{y + oy:.1f}" font-family="\'Avenir Next\', sans-serif" font-size="12" '
            f'fill="{ROSE}">{prefix}{i}</text>'
        )
    return "".join(out)


FLOURISHED = {
    "strokes": [(s[0][:1], *s[1:]) if i == 0 else s for i, s in enumerate(flourish(step=90)["strokes"])],
    "shape_strokes": FLOURISH["strokes"],
    "leaves": [],
    "centre_leaf": FLOURISH["shapes"][0],
}


def write_template(slug, spec, title):
    shape = []
    for segs, wmax, *hair in spec.get("shape_strokes", spec["strokes"]):
        poly = ribbon(segs, wmax, hair=hair[0] if hair else 3.0)
        shape.append(f'<path d="{poly_d(poly)}"/><path d="{poly_d(mirror_poly(poly))}"/>')
    for d in spec["leaves"]:
        shape.append(f'<path d="{d}"/><path d="{mirror_d(d)}"/>')
    if "centre_leaf" in spec:
        shape.append(f'<path d="{spec["centre_leaf"]}"/>')

    guides = (
        f'<line x1="500" y1="40" x2="500" y2="915" stroke="{BRONZE}" stroke-width="1" stroke-dasharray="8 6"/>'
        f'<line x1="120" y1="815" x2="880" y2="815" stroke="{BRONZE}" stroke-width="1" stroke-dasharray="2 6"/>'
        f'<text x="40" y="30" font-family="\'Avenir Next\', sans-serif" font-size="15" fill="{BRONZE}">{title}</text>'
        f'<text font-family="\'Avenir Next\', sans-serif" font-size="15" fill="{BRONZE}">'
        '<tspan x="40" y="945">Trace the rose paths on the left only, one stroke per letter: click the dots in order '
        "(A1, A2…) and drag each handle out to its hollow circle.</tspan>"
        '<tspan x="40" y="968">Then duplicate, Flip Horizontal, and line the copy up on the dashed centre line.</tspan></text>'
    )
    paths = "".join(
        f'<g id="stroke-{"ABCDE"[i]}">{skeleton(segs, "ABCDE"[i])}</g>' for i, (segs, *_) in enumerate(spec["strokes"])
    )
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" width="1000" height="1000">'
        '<rect id="paper" width="1000" height="1000" fill="#fff"/>'
        f'<g id="guides">{guides}</g>'
        f'<g id="shape" fill="{INK}" opacity="0.14">{"".join(shape)}</g>'
        f'<g id="pen-path">{paths}</g>'
        "</svg>"
    )
    with open(os.path.join(HERE, f"{slug}.svg"), "w") as f:
        f.write(svg)


if __name__ == "__main__":
    write_template("template-a-plain", PLAIN, "Plain A: add your own flourishes")
    write_template("template-a-scrolls", SCROLLS, "Scroll A: spirals at the crown, crossbar and feet")
    write_template(
        "template-a-flourished", FLOURISHED, "Flourished A: A leg, B crown loop, C foot swash, D crossbar loop, E outer swash"
    )
