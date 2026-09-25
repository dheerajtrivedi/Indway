"""Turn a panel page's front elevation SVG into a 3D line drawing seen from the top right.

The front drawing is kept as-is and mapped onto the front face of the enclosure with an affine
matrix (an orthographic view of a plane is affine). The right-hand side cover and the roof are
added as their own faces. Faces are filled with the page ground and drawn back to front, so the
edges they cover are hidden, as in a CAD hidden-line view.

    python3 mockups/iso_elev.py lt-panels/pcc-panel/index.html > out.svg
"""
import math
import re
import sys

YAW, PITCH = math.radians(25), math.radians(18)
CY, SY, CP, SP = math.cos(YAW), math.sin(YAW), math.cos(PITCH), math.sin(PITCH)


def proj(p):
    """3D point (x right, y up, z toward the viewer) to SVG screen coordinates (y down)."""
    x, y, z = p
    return (x * CY - z * SY, -(-x * SY * SP + y * CP - z * CY * SP))


def frame(o, ex, ey):
    """SVG matrix() mapping a plane's local 2D coords (origin o, unit axes ex, ey) onto the screen."""
    ox, oy = proj(o)
    ax, ay = proj(ex)
    cx, cy = proj(ey)
    return f"matrix({ax:.4f} {ay:.4f} {cx:.4f} {cy:.4f} {ox:.2f} {oy:.2f})"


def main(path):
    src = open(path, encoding="utf-8").read()
    svg = re.search(r'<svg class="elev" viewBox="([^"]+)"[^>]*aria-label="([^"]+)"[^>]*>(.*?)</svg>', src, re.S)
    body = svg.group(3)
    els = re.findall(r"^\s*(<(?:rect|line|circle)\b[^>]*/>)", body.split('<g class="dims"')[0], re.M)
    solid = [e for e in els if 'class="ln solid"' in e]
    outer = dict(re.findall(r'(x|y|width|height)="([\d.]+)"', solid[0]))
    plinth = dict(re.findall(r'(x|y|width|height)="([\d.]+)"', solid[-1]))
    X0, Y0, BW = float(outer["x"]), float(outer["y"]), float(outer["width"])
    FLOOR = float(plinth["y"]) + float(plinth["height"])
    k = BW / int(re.findall(r"<text[^>]*>(\d+)</text>", body)[-2])  # px per mm, from the overall width figure
    WMM = round(BW / k)
    HMM = int(re.findall(r"<text[^>]*>(\d+)</text>", body)[-1])
    DMM = 1000
    W, H, D, PL, CAP, OV = BW, FLOOR - Y0, DMM * k, float(plinth["height"]), 4, 6
    # Front detail: everything but the floor line, roof line, outer enclosure and plinth
    roofline = re.compile(r'<line class="ln" [^>]*y1="([\d.]+)"[^>]*y2="\1"')
    detail = [e for e in els if 'class="ln floor"' not in e and e not in (solid[0], solid[-1])
              and not ((m := roofline.search(e)) and float(m.group(1)) == Y0)]

    out, n = [], [0]

    def i():
        n[0] += 1
        return n[0]

    def poly(pts, cls="ln solid"):
        s = " ".join(f"{x:.2f},{y:.2f}" for x, y in map(proj, pts))
        out.append(f'<polygon class="{cls}" pathLength="1" style="--i:{i()}" points="{s}"/>')

    def box(x0, x1, y0, y1, z0, z1, side="ln solid shade"):
        poly([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)])            # front
        poly([(x1, y0, z1), (x1, y0, z0), (x1, y1, z0), (x1, y1, z1)], side)      # right side
        poly([(x0, y1, z1), (x1, y1, z1), (x1, y1, z0), (x0, y1, z0)])            # top

    def local(tf, items):
        out.append(f'<g transform="{tf}">')
        for e in items:
            out.append("  " + re.sub(r"--i:\d+", lambda m: f"--i:{i()}", e) if "--i:" in e else "  " + e)
        out.append("</g>")

    # Enclosure: plinth, body, then the front drawing and the side cover on its faces
    box(0, W, 0, PL, -D + 3, -3)
    box(0, W, PL, H - CAP, -D, 0)
    local(frame((-X0, FLOOR, 0), (1, 0, 0), (0, -1, 0)), detail)
    # Right-hand side cover in (depth from front, page y) coords: bolted sheet, vent louvres top and bottom
    sy0, sy1, sd = Y0 + CAP, FLOOR - PL, D
    side = [f'<rect class="ln" pathLength="1" style="--i:0" x="5" y="{sy0 + 5:.1f}" width="{sd - 10:.1f}" height="{sy1 - sy0 - 10:.1f}"/>']
    for yy in [sy0 + 18 + j * 5 for j in range(4)] + [sy1 - 38 + j * 5 for j in range(5)]:
        side.append(f'<line class="ln" pathLength="1" style="--i:0" x1="{sd * .25:.1f}" y1="{yy:.1f}" x2="{sd * .75:.1f}" y2="{yy:.1f}"/>')
    for u in (10, sd - 10):
        for yy in (sy0 + 10, (sy0 + sy1) / 2, sy1 - 10):
            side.append(f'<circle class="ln" pathLength="1" style="--i:0" cx="{u:.1f}" cy="{yy:.1f}" r="1.6"/>')
    local(frame((W, FLOOR, 0), (0, 0, -1), (0, -1, 0)), side)
    # Roof cap, overhanging the body a little all round
    box(-OV / 2, W + OV / 2, H - CAP, H, -D - OV / 2, OV / 2)
    # Section joints across the roof, at the gaps between the section doors in the front drawing
    doors = sorted({(float(a), float(b)) for a, b in re.findall(r'<rect class="ln" [^>]*x="([\d.]+)" y="' + re.escape(f"{Y0 + 6:.1f}") + r'" width="([\d.]+)"', body)})
    edges = sorted({round(x + w, 1) for x, w in doors})
    joints = [e + 3 - X0 for e in edges if e < X0 + BW - 10]
    roof = [f'<line class="ln" pathLength="1" style="--i:0" x1="{x:.1f}" y1="0" x2="{x:.1f}" y2="{D:.1f}"/>' for x in joints]
    local(frame((0, H, 0), (1, 0, 0), (0, 0, -1)), roof)
    # Lifting eyebolts at the lineup's corners
    for x, z in [(10, -D + 10), (W - 10, -D + 10), (10, -10), (W - 10, -10)]:
        bx, by = proj((x, H, z))
        out.append(f'<line class="ln" pathLength="1" style="--i:{i()}" x1="{bx:.2f}" y1="{by:.2f}" x2="{bx:.2f}" y2="{by - 4:.2f}"/>')
        out.append(f'<circle class="ln solid" pathLength="1" style="--i:{i()}" cx="{bx:.2f}" cy="{by - 7.2:.2f}" r="3.2"/>')

    # Overall dimensions: width along the front, depth along the right side, height at the back right corner
    dims, fs = [], 13
    def dim(a, b, off, label):
        (ax, ay), (bx, by) = proj(a), proj(b)
        oa = proj(tuple(p + q for p, q in zip(a, off)))
        ob = proj(tuple(p + q for p, q in zip(b, off)))
        ux, uy = ob[0] - oa[0], ob[1] - oa[1]
        L = math.hypot(ux, uy); ux, uy = ux / L, uy / L
        ex, ey = oa[0] - ax, oa[1] - ay
        el = math.hypot(ex, ey); ex, ey = ex / el, ey / el
        for (px, py), (qx, qy) in (((ax, ay), oa), ((bx, by), ob)):
            dims.append(f'<line class="ext" x1="{px + ex * 3:.1f}" y1="{py + ey * 3:.1f}" x2="{qx + ex * 4:.1f}" y2="{qy + ey * 4:.1f}"/>')
        dims.append(f'<line x1="{oa[0]:.1f}" y1="{oa[1]:.1f}" x2="{ob[0]:.1f}" y2="{ob[1]:.1f}"/>')
        for (px, py), s in ((oa, 1), (ob, -1)):
            tx, ty, nx, ny = px + s * ux * 5.2, py + s * uy * 5.2, -uy * 1.9, ux * 1.9
            dims.append(f'<polygon class="arrow" points="{px:.1f},{py:.1f} {tx + nx:.1f},{ty + ny:.1f} {tx - nx:.1f},{ty - ny:.1f}"/>')
        ang = math.degrees(math.atan2(uy, ux))
        if ang > 90: ang -= 180
        if ang < -90: ang += 180
        mx, my = (oa[0] + ob[0]) / 2 + ex * 8, (oa[1] + ob[1]) / 2 + ey * 8 + fs * .35
        dims.append(f'<text x="{mx:.1f}" y="{my:.1f}" transform="rotate({ang:.1f} {mx:.1f} {my - fs * .35:.1f})">{label}</text>')
        return [oa, ob]

    ends = []
    ends += dim((0, 0, 0), (W, 0, 0), (0, 0, 26), WMM)
    ends += dim((W, 0, 0), (W, 0, -D), (26, 0, 0), DMM)
    ends += dim((W + OV / 2, 0, -D), (W + OV / 2, H, -D), (24, 0, 0), HMM)

    # viewBox round everything drawn, with a margin for strokes and labels
    pts = [proj((x, y, z)) for x in (-OV, W + OV) for y in (0, H + 12) for z in (OV, -D - OV)] + ends
    x0 = min(p[0] for p in pts) - 22; x1 = max(p[0] for p in pts) + 16
    y0 = min(p[1] for p in pts) - 14; y1 = max(p[1] for p in pts) + 16
    label = svg.group(2).replace("Front elevation line drawing", "3D line drawing, seen from the front right,")
    print(f'<svg class="elev elev--iso" viewBox="{x0:.1f} {y0:.1f} {x1 - x0:.1f} {y1 - y0:.1f}" role="img" aria-label="{label}, showing the side cover and roof">')
    for e in out:
        print("  " + e)
    print(f'  <g class="dims" style="--fs:{fs}" aria-hidden="true">')
    for e in dims:
        print("    " + e)
    print("  </g>\n</svg>")


main(sys.argv[1])
