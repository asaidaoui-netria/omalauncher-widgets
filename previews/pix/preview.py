"""Pix with a headset: renders a few poses from the widget's own sprites. python3 previews/pix/preview.py OUT.png"""
import re, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pierrot"))
from sim import Canvas, PAL, mix, alpha_over

src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "widgets", "20-fetch.owl")).read()
def spr(name):
    m = re.search(r"let %s = \[(.*?)\]" % name, src, re.S)
    return re.findall(r'"([^"]*)"', m.group(1))
body, aRL, aRR, aUL, aUR, bulb = (spr(n) for n in ("botBody", "armRestL", "armRestR", "armUpL", "armUpR", "bulbArt"))
HEADSET = [
    "....bbbbbbbbbbbbbbbbbbbbbb....",
    "..bbhhhhhhhhhhhhhhhhhhhhhhbb..",
    ".bh........................hb.",
    ".bh........................hb.",
    ".cc........................cc.",
    "cppc......................cppc",
    "cppc......................cppc",
    "cppc......................cppc",
    "cppc......................cppc",
    ".cc........................cc.",
]
MIC = [
    "..m...........................",
    "...m..........................",
    "....mMM.......................",
    ".....MM.......................",
]
assert all(len(r) == 30 for r in HEADSET)

def put(c, art, x, y, pal):
    for j, row in enumerate(art):
        for i, ch in enumerate(row):
            if ch in pal and 0 <= x + i < c.w and 0 <= y + j < c.h:
                col, a = pal[ch] if isinstance(pal[ch], tuple) and len(pal[ch]) == 2 else (pal[ch], 1)
                c.px[y + j][x + i] = alpha_over(c.px[y + j][x + i], col, a)

def pix(c, ox, pose, headset, hpal):
    acc, bg, fg = PAL["accent"], PAL["background"], PAL["foreground"]
    shade, hand = mix(acc, bg, 0.55), mix(acc, fg, 0.35)
    bx, ty = ox + 13, 14
    up = pose == "dance"
    put(c, aUL if up else aRL, bx - 4, ty + 3 if up else ty + 9, {"o": shade, "h": hand})
    put(c, aUR if up else aRR, bx + 26, ty + 3 if up else ty + 9, {"o": shade, "h": hand})
    if headset:
        put(c, HEADSET[:4], bx - 2, ty - 3, hpal)   # band behind the antenna
    for k in range(4):
        c.rect(bx + 12, ty - 4 + k, 2, 1, shade)
    put(c, bulb, bx + 11, ty - 8, {"l": PAL["green"], "w": fg})
    put(c, body, bx, ty, {"o": shade, "b": acc, "h": hand, "d": mix(acc, bg, 0.25), "k": mix(bg, acc, 0.18), "s": bg,
                          "g": (fg, 0.45), "x": shade, "v": shade, "r": PAL["magenta"]})
    glow = PAL["green"] if up else PAL["cyan"]
    eyes = ["...", ".e.", "e.e", "..."] if up else ["wee", "eee", "eee", "eee"]
    put(c, eyes, bx + 7, ty + 5, {"e": glow, "w": fg})
    put(c, eyes, bx + 16, ty + 5, {"e": glow, "w": fg})
    put(c, ["eeeeee", "e.rr.e", ".eeee."] if up else ["e....e", ".eeee."], bx + 10, ty + 9 if up else ty + 10, {"e": glow, "r": PAL["red"]})
    if headset:
        put(c, HEADSET[4:], bx - 2, ty + 1, hpal)
        if hpal.get("mic"): put(c, MIC, bx - 2, ty + 7, hpal)
    for lx in (6, 17):
        c.rect(bx + lx + 1, ty + 20, 2, 2, shade); c.rect(bx + lx, ty + 22, 4, 1, shade)

bgp = alpha_over(PAL["background"], PAL["foreground"], 0.05)
variants = [
    ("none", None),
    ("dark+green", {"b": mix(PAL["background"], PAL["foreground"], 0.3), "h": mix(PAL["background"], PAL["foreground"], 0.5), "c": mix(PAL["background"], PAL["foreground"], 0.3), "p": PAL["green"], "m": mix(PAL["background"], PAL["foreground"], 0.3), "M": PAL["green"]}),
    ("dark+green+mic", {"b": mix(PAL["background"], PAL["foreground"], 0.3), "h": mix(PAL["background"], PAL["foreground"], 0.5), "c": mix(PAL["background"], PAL["foreground"], 0.3), "p": PAL["green"], "m": mix(PAL["background"], PAL["foreground"], 0.3), "M": mix(PAL["background"], PAL["foreground"], 0.3), "mic": 1}),
    ("muted+green+mic", {"b": PAL["muted"], "h": mix(PAL["muted"], PAL["foreground"], 0.35), "c": PAL["muted"], "p": PAL["green"], "m": PAL["muted"], "M": PAL["muted"], "mic": 1}),
]
c = Canvas(52 * len(variants) * 2, 40, bgp)
for n, (name, hp) in enumerate(variants):
    for k, pose in enumerate(("idle", "dance")):
        pix(c, (n * 2 + k) * 52, pose, hp is not None, hp or {})
os.makedirs(os.path.dirname(sys.argv[1]) or ".", exist_ok=True)
c.save(sys.argv[1], 6)
print("variants:", [v[0] for v in variants])
