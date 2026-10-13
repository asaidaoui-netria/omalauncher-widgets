"""Pierrot v2: sprites, rig and a renderer that mirrors the widget's drawing, for previews without the phone.

The OWL code in the widget is a line-by-line port of draw_* here; keep the two in step.
"""
import math, os, subprocess

PAL = {  # Tokyo Night, the phone's theme
    "background": (0x1a, 0x1b, 0x26), "foreground": (0xc0, 0xca, 0xf5), "accent": (0x7a, 0xa2, 0xf7),
    "muted": (0x56, 0x5f, 0x89), "red": (0xf7, 0x76, 0x8e), "yellow": (0xe0, 0xaf, 0x68), "cyan": (0x7d, 0xcf, 0xff),
    "blue": (0x7a, 0xa2, 0xf7), "magenta": (0xbb, 0x9a, 0xf7), "orange": (0xff, 0x9e, 0x64), "green": (0x9e, 0xce, 0x6a),
}


def mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def alpha_over(dst, src, a):
    return tuple(round(dst[i] + (src[i] - dst[i]) * a) for i in range(3))


BG, FG = PAL["background"], PAL["foreground"]
# Pierrot's colors: o outline, w costume, s fold shade, k cap/buttons/slippers, r lips, t tear, c blush, f face shade.
PIERROT = {
    "o": mix(BG, (0, 0, 0), 0.45), "w": mix(FG, (255, 255, 255), 0.55), "s": mix(FG, BG, 0.28),
    "k": mix(BG, (0, 0, 0), 0.4), "h": mix(BG, FG, 0.38), "r": PAL["red"], "t": PAL["cyan"], "c": mix(PAL["red"], (255, 255, 255), 0.35),
    "f": mix(FG, (255, 255, 255), 0.25),
}

S = {}
# The head without eyes or mouth: skullcap, white face, a little shading on the right.
S["head"] = [
    "....ooooo....",
    "..ookhhkkoo..",
    ".okkhkkkkkko.",
    ".okhkkkkkkko.",
    "okkkkkkkkkkko",
    "okkwwwwwwwkko",
    "owwwwwwwwwwwo",
    "owwwwwwwwwwwo",
    "owwwwwwwwwwfo",
    "owwwwwwwwwwfo",
    ".owwwwwwwwfo.",
    "..owwwwwwfo..",
    "...ooooooo...",
]
# Brows (light grey) and eyes: 9x4 at head (2, 6). Sad brows rise toward the middle; eyes are two cells tall.
S["eyes"] = {
    "open":  ["..s...s..", ".s.....s.", "..k...k..", "..k...k.."],
    "shut":  ["..s...s..", ".s.....s.", ".........", ".kk...kk."],
    "left":  ["..s...s..", ".s.....s.", ".k...k...", ".k...k..."],
    "right": ["..s...s..", ".s.....s.", "...k...k.", "...k...k."],
    "down":  ["..s...s..", ".s.....s.", ".........", "..k...k.."],
    "up":    [".ss...ss.", "..k...k..", "..k...k..", "........."],
    "wide":  [".s.....s.", "..s...s..", ".kk...kk.", ".kk...kk."],
    "happy": ["..s...s..", ".........", "..k...k..", ".k.k.k.k."],
    "droop": ["..s...s..", ".s.....s.", ".kk...kk.", "..k...k.."],
}
# Mouth: 3x2 at head (5, 10), under the nose line.
S["mouth"] = {
    "pout":  [".r.", "..."],
    "smile": ["r.r", ".r."],
    "o":     ["rrr", "rkr"],
    "sing":  ["rkr", ".r."],
    "yawn":  ["rkr", "rkr"],
    "flat":  ["rrr", "..."],
}
# The ruff: a pleated collar, 17x4, round the neck.
S["ruff"] = [
    ".oo.ooo.ooo.ooo.",
    "owwswwswwswwswwo",
    "oswwswwswwswwswo",
    ".oooooooooooooo.",
]
# The smock: loose and flaring, with two pompom buttons and folds.
S["torso"] = [
    "....owwwwwwwo....",
    "...owwwwwwwwwo...",
    "...owswwkkwwswo..",
    "..owwswwkkwwswwo.",
    "..owwswwwwwwswwo.",
    "..owswwwkkwwwswo.",
    ".owwswwwkkwwwswwo",
    ".owwswwwwwwwwswwo",
    ".owswwwwkkwwwwswo",
    "owwswwwwkkwwwwswwo"[:17],
    "owswwwwwwwwwwwswo",
    "owwwwwwwwwwwwwwwo",
    ".ooooooooooooooo.",
]


def check_sprites():
    for name, art in S.items():
        if isinstance(art, dict):
            for k, rows in art.items():
                assert len({len(r) for r in rows}) == 1, (name, k)
        else:
            assert len({len(r) for r in art}) == 1, (name, [len(r) for r in art])


class Canvas:
    def __init__(self, w, h, fill):
        self.w, self.h = w, h
        self.px = [[fill] * w for _ in range(h)]

    def rect(self, x, y, w, h, color, a=1.0):
        for yy in range(int(round(y)), int(round(y + h))):
            for xx in range(int(round(x)), int(round(x + w))):
                if 0 <= xx < self.w and 0 <= yy < self.h:
                    self.px[yy][xx] = alpha_over(self.px[yy][xx], color, a) if a < 1 else color

    def sprite(self, rows, x, y, pal, k=1):
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch in pal:
                    self.rect(x + i * k, y + j * k, k, k, pal[ch])

    def save(self, path, scale=6):
        """PPM with each cell as scale x scale pixels and a darker grid line, like the widget's dot matrix."""
        W, H = self.w * scale, self.h * scale
        out = bytearray()
        gap = mix(BG, (0, 0, 0), 0.2)
        for Y in range(H):
            for X in range(W):
                c = self.px[Y // scale][X // scale]
                if X % scale == 0 or Y % scale == 0:
                    c = alpha_over(c, BG, 0.55)
                out += bytes(c)
        ppm = path.replace(".png", ".ppm")
        with open(ppm, "wb") as f:
            f.write(b"P6 %d %d 255\n" % (W, H) + bytes(out))
        subprocess.run(["magick", ppm, path], check=True)
        os.remove(ppm)


def seg_points(x0, y0, x1, y1):
    """Cells of a line between two whole-cell endpoints (as the widget computes them)."""
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    return [(x0 + math.floor((x1 - x0) * i / n + 0.5), y0 + math.floor((y1 - y0) * i / n + 0.5)) for i in range(n + 1)]


def joint(x, y, ang, length):
    """End of a limb from (x, y) at ang degrees (0 down, 90 right, 180 up), rounded to whole cells."""
    return x + math.floor(math.sin(math.radians(ang)) * length + 0.5), y + math.floor(math.cos(math.radians(ang)) * length + 0.5)


def draw_limb(c, pts, cuff):
    """A baggy sleeve or trouser leg through the joint points: outline pass, then fill, then the cuff/foot."""
    cells = []
    for a, b in zip(pts, pts[1:]):
        cells += seg_points(*a, *b)
    for (x, y) in cells:
        c.rect(x - 2, y - 1, 5, 3, PIERROT["o"])
        c.rect(x - 1, y - 2, 3, 5, PIERROT["o"])
    for (x, y) in cells:
        c.rect(x - 1, y - 1, 3, 3, PIERROT["w"])
    ex, ey = pts[-1]
    if cuff == "hand":
        c.rect(ex - 2, ey - 2, 5, 5, PIERROT["o"])
        c.rect(ex - 1, ey - 1, 3, 3, PIERROT["s"])
        c.rect(ex, ey, 1, 1, PIERROT["f"])
    if cuff == "foot":
        c.rect(ex - 2, ey, 5, 3, PIERROT["o"])
        c.rect(ex - 1, ey + 1, 3, 1, PIERROT["k"])


def draw_pierrot(c, hx, hy, j, eyes="open", mouth="pout", hdx=0, hdy=0, blush=False):
    """Pierrot with hips at (hx, hy). j: joint angles uaL faL uaR faR thL shL thR shR (degrees)."""
    hx, hy = round(hx), round(hy)
    # Legs first (behind the smock), then the body, head and ruff, then the arms in front.
    for side, th, sh in ((-1, j["thL"], j["shL"]), (1, j["thR"], j["shR"])):
        h0 = (hx + 3 * side, hy)
        kn = joint(*h0, th, 4)
        ft = joint(*kn, sh, 4)
        draw_limb(c, [h0, kn, ft], "foot")
    c.sprite(S["torso"], hx - 8, hy - 11, PIERROT)
    c.sprite(S["head"], hx - 6 + hdx, hy - 25 + hdy, PIERROT)
    c.sprite(S["eyes"][eyes], hx - 4 + hdx, hy - 19 + hdy, PIERROT)
    c.sprite(S["mouth"][mouth], hx - 1 + hdx, hy - 14 + hdy, PIERROT)
    c.rect(hx + 2 + hdx, hy - 15 + hdy, 1, 1, PIERROT["t"])  # the tear, under his left eye
    if blush:
        c.rect(hx - 4 + hdx, hy - 15 + hdy, 1, 1, PIERROT["c"])
        c.rect(hx + 4 + hdx, hy - 15 + hdy, 1, 1, PIERROT["c"])
    c.sprite(S["ruff"], hx - 8, hy - 13, PIERROT)
    for side, ua, fa in ((-1, j["uaL"], j["faL"]), (1, j["uaR"], j["faR"])):
        sh = (hx + 6 * side, hy - 10)
        el = joint(*sh, ua, 5)
        hd = joint(*el, fa, 5)
        draw_limb(c, [sh, el, hd], "hand")


STAND = dict(uaL=-25, faL=-10, uaR=25, faR=10, thL=-6, shL=0, thR=6, shR=0)

SKY = mix(BG, PAL["blue"], 0.16)
MOONC = mix(PAL["yellow"], FG, 0.6)

if __name__ == "__main__":
    check_sprites()
    os.makedirs("out", exist_ok=True)
    c = Canvas(96, 44, SKY)
    for y in range(44):
        for x in range(56, 96):
            if (x - 82) ** 2 + (y - 22) ** 2 <= 19.5 ** 2:
                c.rect(x, y, 1, 1, MOONC)
    draw_pierrot(c, 22, 30, STAND)
    draw_pierrot(c, 72, 30, dict(uaL=-130, faL=-165, uaR=125, faR=160, thL=-12, shL=-4, thR=12, shR=4), eyes="up", mouth="sing", blush=True)
    c.save("out/still2.png", 7)
    print("ok")
