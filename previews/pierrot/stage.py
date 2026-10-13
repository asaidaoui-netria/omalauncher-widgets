"""The moon stage (160x72 cells): sky, stars, moon and Paris rooftops, with a scene on top (fish.py, scenes.py).
Mirrors the widget's OWL."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sim import Canvas, PAL, BG, FG, mix, alpha_over, PIERROT, S, draw_pierrot, seg_points, joint

W, H = 160, 72
SKY = [mix(BG, PAL["blue"], k) for k in (0.08, 0.12, 0.16, 0.2)]
MOON_L = mix(PAL["yellow"], FG, 0.6)
MOON_M = mix(MOON_L, BG, 0.12)
STAR = PAL["yellow"]
STARS = [(6, 5), (19, 14), (31, 4), (44, 20), (58, 8), (70, 17), (83, 3), (97, 12), (141, 6), (152, 18), (11, 30), (67, 33), (149, 33), (38, 38), (89, 26)]
MARES = [(13, 13, 5), (23, 10, 4), (26, 20, 5), (15, 25, 6), (27, 29, 3)]


def moon_rows(elong, lat=34.3):
    """The moon at 39x39: l lit, m maria, d the earthshine side."""
    ct = math.cos(math.radians(elong))
    sgn = (1 if elong < 180 else -1) * (-1 if lat < 0 else 1)
    rows = []
    for j in range(39):
        r = ""
        for i in range(39):
            dx, dy = i - 19, j - 19
            if dx * dx + dy * dy > 380.25:
                r += "."
            elif sgn * dx > math.sqrt(max(0, 380.25 - dy * dy)) * ct:
                r += "m" if any((i - a) ** 2 + (j - b) ** 2 <= c * c for a, b, c in MARES) else "l"
            else:
                r += "d"
        rows.append(r)
    return rows


def skyline():
    """Paris rooftops, 160x16 from y=56: b facade, e zinc roof and edges, c chimney stacks. Windows come separately."""
    g = [["." for _ in range(W)] for _ in range(16)]
    wins = []
    # (x0, x1, roof top row): each block gets a mansard roof, dormers, a chimney stack or two, and windows.
    blocks = [(0, 15, 7), (15, 30, 5), (30, 100, 4), (100, 124, 4), (124, 142, 7), (142, 160, 5)]
    for n, (x0, x1, top) in enumerate(blocks):
        for x in range(x0, x1):
            edge = min(x - x0, x1 - 1 - x)
            t0 = top + max(0, 2 - edge)          # the mansard's sloped ends
            for y in range(t0, 16):
                g[y][x] = "b"
            for y in range(t0, min(top + 3, 16)):  # the zinc roof itself
                g[y][x] = "e"
        # Dormers on the roof: a little gable with a window.
        for dx in range(x0 + 4, x1 - 4, 6 if x1 - x0 < 40 else 13):
            g[top - 1][dx + 1] = "e"
            for y in range(top, top + 3):
                g[y][dx] = "b"; g[y][dx + 1] = "b"; g[y][dx + 2] = "b"
            wins.append((dx + 1, top + 1, (dx * 7 + n) % 9))
        # Chimney stacks with pots.
        for cx in ((x0 + 2,) if x1 - x0 < 19 else (51, 76) if x0 == 30 else (x0 + 2, x1 - 7)):
            for y in range(top - 3, top):
                for x in range(cx, cx + 4):
                    g[y][x] = "c"
            g[top - 4][cx] = "c"; g[top - 4][cx + 2] = "c"
        # Two rows of tall windows on the facade.
        for wx in range(x0 + 3, x1 - 2, 4):
            for wy in (top + 5, top + 10):
                if wy + 1 < 16:
                    wins.append((wx, wy, (wx * 5 + wy * 3 + n) % 9))
    return ["".join(r) for r in g], wins


ROOFS, WINDOWS = skyline()
ROOF_PAL = {"b": mix(BG, PAL["blue"], 0.26), "e": mix(BG, PAL["blue"], 0.42), "c": mix(BG, PAL["blue"], 0.34)}
TOWER = [
    ".....h.....",
    ".....h.....",
    ".....h.....",
    "....hhh....",
    "....hhh....",
    "....h.h....",
    "...hhhhh...",
    "...h...h...",
    "...h...h...",
    "...h...h...",
    "..hh...hh..",
    "..hhhhhhh..",
    "..h.....h..",
    ".hh.....hh.",
    ".h..hhh..h.",
    ".h.h...h.h.",
    "hh.......hh",
    "h.........h",
]


def draw_city(c, t):
    c.sprite(TOWER, 22, 60 - len(TOWER), {"h": mix(BG, PAL["blue"], 0.3)})
    c.sprite(ROOFS, 0, 56, ROOF_PAL)
    for (x, y, ph) in WINDOWS:
        # Most windows are lit or dark for good; a few come on and go off now and then.
        lit = ph < 3 or (ph == 8 and (t / 7 + x) % 3 < 1.6)
        if lit:
            c.rect(x, 56 + y, 1, 2, mix(PAL["yellow"], FG, 0.25) if ph != 1 else mix(PAL["orange"], FG, 0.3))


def smooth(f):
    return f * f * (3 - 2 * f)


def keyframe(keys, t):
    """Eased interpolation between keyframes; discrete fields come from the current key."""
    i = max(k for k in range(len(keys)) if keys[k]["t"] <= t)
    a, b = keys[i], keys[min(i + 1, len(keys) - 1)]
    f = 0 if b["t"] == a["t"] else smooth((t - a["t"]) / (b["t"] - a["t"]))
    out = {}
    for k, v in a.items():
        out[k] = v + (b[k] - v) * f if isinstance(v, (int, float)) else v
    return out


def K(t, **kw):
    base = dict(uaL=-40, faL=-120, uaR=20, faR=-60, thL=-82, shL=-8, thR=82, shR=8, hdx=0, hdy=0, rod=-135, L=30,
                eyes="down", mouth="pout")
    base.update(kw)
    base["t"] = t
    return base


def star_sprite(c, x, y, color, big=False):
    if big:
        for dx, dy in ((0, -2), (-1, -1), (0, -1), (1, -1), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (-1, 1), (1, 1)):
            c.rect(round(x) + dx, round(y) + dy, 1, 1, color)
    else:
        for dx, dy in ((0, -1), (-1, 0), (0, 0), (1, 0), (0, 1)):
            c.rect(round(x) + dx, round(y) + dy, 1, 1, color)


def render(t, elong=26, scene=None):
    c = Canvas(W, H, SKY[0])
    for b in range(4):
        c.rect(0, b * 14, W, 14 if b < 3 else H - 42, SKY[b])
    for n, (x, y) in enumerate(STARS):
        a = 0.25 + 0.6 * abs(math.sin(t * 1.1 + n * 1.7))
        c.rect(x, y, 1, 1, alpha_over(c.px[y][x], FG, a))
    mx, my = 116, 47
    pal = {"l": MOON_L, "m": MOON_M}
    rows = moon_rows(elong)
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            x, y = mx - 19 + i, my - 19 + j
            if 0 <= x < W and 0 <= y < H:
                if ch in pal:
                    c.px[y][x] = pal[ch]
                elif ch == "d":
                    c.px[y][x] = alpha_over(c.px[y][x], FG, 0.1)
    draw_city(c, t)
    if scene:
        scene(c, t)
    return c


