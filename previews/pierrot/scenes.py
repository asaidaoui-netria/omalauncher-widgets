"""Pierrot's other five phases, for the previewer. The widget's OWL is a port of these; keep them in step."""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sim import PAL, BG, FG, mix, alpha_over, PIERROT, draw_pierrot, seg_points, joint
from stage import keyframe, smooth, star_sprite

STANDJ = dict(uaL=-22, faL=-8, uaR=22, faR=8, thL=-6, shL=0, thR=6, shR=0)


def KJ(t, base=None, **kw):
    k = dict(base or STANDJ, hx=0, hy=0, hdx=0, hdy=0, walk=0, eyes="open", mouth="pout")
    k.update(kw)
    k["t"] = t
    return k


def fr(v):
    return math.floor(v + 0.5)


# ---- seek (new moon): pacing the roof with a lantern on a pole, looking for the missing moon (16 s). ----
SEEK = [
    KJ(0.0, hx=42, walk=1, eyes="right", uaR=115, faR=150),
    KJ(5.0, hx=86, walk=1, eyes="right", uaR=115, faR=150),
    KJ(5.5, hx=88, walk=0, eyes="up", uaR=150, faR=172, mouth="o"),                  # stops, lifts the lantern high
    KJ(6.6, hx=88, eyes="up", uaR=150, faR=172, mouth="o"),
    KJ(7.2, hx=88, eyes="left", uaR=115, faR=150, uaL=-150, faL=120, mouth="flat"),  # scratches his head
    KJ(8.2, hx=88, eyes="right", uaR=115, faR=150, uaL=-150, faL=120, mouth="flat"),
    KJ(8.8, hx=88, eyes="open", uaR=120, faR=140, uaL=-75, faL=-120, mouth="flat"),  # shrugs at us
    KJ(9.6, hx=88, eyes="open", uaR=120, faR=140, uaL=-75, faL=-120, mouth="flat"),
    KJ(10.0, hx=86, walk=1, eyes="left", uaR=115, faR=150),
    KJ(15.0, hx=44, walk=1, eyes="left", uaR=115, faR=150),
    KJ(15.4, hx=42, walk=0, eyes="up", uaR=150, faR=172),
    KJ(16.0, hx=42, walk=1, eyes="right", uaR=115, faR=150),
]


def scene_seek(c, t):
    tl = t % 16
    k = keyframe(SEEK, tl)
    w = k["walk"]
    ph = t * 7
    k["thL"] += w * 24 * math.sin(ph)
    k["thR"] -= w * 24 * math.sin(ph)
    k["shL"] = k["thL"] * 0.4 - w * 10 * max(0, math.sin(ph))
    k["shR"] = k["thR"] * 0.4 - w * 10 * max(0, -math.sin(ph))
    hx, hy = fr(k["hx"]), 50 - fr(w * abs(math.sin(ph)))
    eyes = "shut" if k["eyes"] in ("open", "left", "right") and t % 3.3 < 0.12 else k["eyes"]
    draw_pierrot(c, hx, hy, k, eyes=eyes, mouth=k["mouth"], hdx=0, hdy=0)
    # The pole from his right hand, the lantern swinging below its tip, and its flickering glow.
    sh = (hx + 6, hy - 10)
    hand = joint(*joint(*sh, k["uaR"], 5), k["faR"], 5)
    tip = joint(*hand, 178, 9)
    for (x, y) in seg_points(*hand, *tip):
        c.rect(x, y, 1, 1, mix(PAL["orange"], BG, 0.4))
    sw = 14 * math.sin(t * 3.1) + w * 9 * math.sin(ph)
    lx, ly = joint(*tip, sw, 3)
    glow = 0.16 + 0.1 * abs(math.sin(t * 9)) + 0.05 * math.sin(t * 2.3)
    for r in (6, 4):
        for dy in range(-r, r + 1):
            hw = math.floor(math.sqrt(r * r - dy * dy))
            c.rect(lx - hw, ly + 2 + dy, 2 * hw + 1, 1, PAL["yellow"], glow * (0.6 if r == 6 else 1))
    c.rect(lx, ly, 1, 1, PIERROT["o"])
    c.rect(lx - 1, ly + 1, 3, 1, PIERROT["o"])
    c.rect(lx - 1, ly + 2, 3, 2, PAL["yellow"])
    c.rect(lx - 1, ly + 4, 3, 1, PIERROT["o"])


# ---- play (first quarter to gibbous): on a chimney, strumming a mandolin, foot tapping (10 s). ----
SEATJ = dict(uaL=-20, faL=-75, uaR=25, faR=-65, thL=-82, shL=-10, thR=82, shR=10)
PLAY = [
    KJ(0.0, SEATJ, eyes="shut", mouth="sing", strum=1),
    KJ(3.0, SEATJ, eyes="open", mouth="smile", strum=1),
    KJ(5.0, SEATJ, eyes="shut", mouth="sing", strum=1, hdx=1),
    KJ(6.8, SEATJ, eyes="shut", mouth="sing", strum=1),
    KJ(7.2, dict(SEATJ, uaR=120, faR=165), eyes="happy", mouth="o", strum=0),         # flourish: winds up...
    KJ(7.7, dict(SEATJ, uaR=10, faR=-40), eyes="happy", mouth="sing", strum=0),        # ...and sweeps down
    KJ(8.4, SEATJ, eyes="happy", mouth="smile", strum=1),
    KJ(10.0, SEATJ, eyes="shut", mouth="sing", strum=1),
]
MANDOLIN = [
    "oo..............",
    "omoo......ooooo.",
    ".ommoo...ommmmmo",
    "..oommoooommnnmmo"[:16],
    "....oommmmmnnnmo",
    "......ommmmmnmmo",
    ".......ommmmmmo.",
    "........oooooo..",
]
MPAL = {"o": PIERROT["o"], "m": mix(PAL["orange"], BG, 0.15), "n": mix(BG, (0, 0, 0), 0.3)}
NOTE = ["..yy", "..y.", "yyy.", "yy.."]


def scene_play(c, t):
    tl = t % 10
    k = keyframe(PLAY, tl)
    beat = t * 2.2
    s = k["strum"]
    k["faR"] += s * 26 * math.sin(t * 13)
    k["uaR"] += s * 6 * math.sin(t * 13)
    k["shR"] += 22 * max(0, math.sin(beat * math.pi))      # tapping his foot on the beat
    k["shL"] += 6 * math.sin(t * 1.3)
    hx, hy = 53, 56
    hdy = fr(0.5 + 0.5 * math.sin(beat * math.pi * 2 - 1))
    draw_pierrot(c, hx, hy, k, eyes=k["eyes"], mouth=k["mouth"], hdx=fr(k["hdx"]), hdy=hdy, blush=k["mouth"] in ("smile", "sing"))
    # The mandolin across his lap, over the arms' roots; the strumming hand is drawn again on top.
    c.sprite(MANDOLIN, hx - 13, hy - 9, MPAL)
    sh = (hx + 6, hy - 10)
    el = joint(*sh, k["uaR"], 5)
    hd = joint(*el, k["faR"], 5)
    from sim import draw_limb
    draw_limb(c, [sh, el, hd], "hand")
    for n in range(3):
        u = (t * 0.45 + n / 3) % 1
        x = fr(hx - 2 + n * 4 + 8 * u + 2 * math.sin(t * 2 + n * 2))
        y = fr(hy - 14 - 30 * u)
        col = alpha_over(c.px[max(y, 0)][max(0, min(159, x))], (PAL["yellow"], PAL["magenta"], PAL["cyan"])[n], 1 - u)
        c.sprite(NOTE, x, y, {"y": col})


# ---- serenade (full moon): a little routine on the roof for the glowing moon (12 s). ----
SER = [
    KJ(0.0, uaL=-105, faL=-125, uaR=110, faR=140, eyes="up", mouth="sing"),           # arms open to the moon
    KJ(1.8, uaL=-110, faL=-135, uaR=115, faR=150, eyes="up", mouth="sing", hdx=1),
    KJ(2.4, uaL=-20, faL=-10, uaR=25, faR=-105, eyes="shut", mouth="pout", hdx=1),    # hand on his heart
    KJ(3.6, uaL=-20, faL=-10, uaR=25, faR=-105, eyes="shut", mouth="pout", hdx=1),
    KJ(4.2, uaL=60, faL=95, uaR=100, faR=120, thL=-35, shL=-5, thR=35, shR=5, hy=3, eyes="up", mouth="o"),  # kneels, pleading
    KJ(5.6, uaL=65, faL=100, uaR=105, faR=125, thL=-35, shL=-5, thR=35, shR=5, hy=3, eyes="up", mouth="o"),
    KJ(6.3, eyes="open", mouth="pout"),                                                 # gets up
    KJ(6.8, uaL=-150, faL=-170, uaR=115, faR=150, hy=1, eyes="happy", mouth="smile"),  # crouch...
    KJ(7.15, uaL=-165, faL=-178, uaR=150, faR=172, hy=-4, thL=-14, thR=14, eyes="happy", mouth="smile"),  # ...hop!
    KJ(7.5, eyes="happy", mouth="smile"),
    KJ(8.2, uaR=25, faR=-150, eyes="shut", mouth="o"),                                  # kisses his hand...
    KJ(8.8, uaR=115, faR=120, eyes="happy", mouth="smile"),                             # ...and blows it to the moon
    KJ(9.8, uaR=60, faR=60, eyes="happy", mouth="smile"),
    KJ(10.3, uaL=-40, faL=20, uaR=40, faR=-20, hdy=2, eyes="shut", mouth="smile"),       # bows
    KJ(11.2, uaL=-40, faL=20, uaR=40, faR=-20, hdy=2, eyes="shut", mouth="smile"),
    KJ(12.0, uaL=-105, faL=-125, uaR=110, faR=140, eyes="up", mouth="sing"),
]
HEART = [".y.y.", "yyyyy", ".yyy.", "..y.."]


def scene_serenade(c, t, mx=118, my=30):
    tl = t % 12
    k = keyframe(SER, tl)
    hx, hy = 52, 50 + fr(k["hy"])
    draw_pierrot(c, hx, hy, k, eyes=k["eyes"], mouth=k["mouth"], hdx=fr(k["hdx"]), hdy=fr(k["hdy"]), blush=k["mouth"] == "smile")
    if tl < 2.2 or 4.2 <= tl < 5.6:
        for n in range(2):
            u = (t * 0.5 + n / 2) % 1
            x, y = fr(hx + 4 + 20 * u), fr(hy - 26 - 12 * u + 2 * math.sin(t * 3 + n))
            c.sprite(NOTE, x, y, {"y": alpha_over(c.px[max(0, y)][min(159, x)], PAL["yellow"], 1 - u)})
    if 8.8 <= tl < 10.2:
        u = (tl - 8.8) / 1.4
        x = fr(hx + 10 + (mx - hx - 12) * u)
        y = fr(hy - 14 + (my - hy + 12) * u - 10 * math.sin(u * math.pi))
        c.sprite(HEART, x - 2, y - 2, {"y": PAL["red"]})


# ---- doze (waning): sitting on the roof against the moon, nodding off, startled awake, yawning (12 s). ----
SITJ = dict(uaL=-12, faL=55, uaR=12, faR=-55, thL=-82, shL=-6, thR=82, shR=6)
DOZE = [
    KJ(0.0, SITJ, eyes="shut", hdx=1, hdy=1),
    KJ(4.4, SITJ, eyes="shut", hdx=1, hdy=2),
    KJ(5.0, SITJ, eyes="shut", hdx=1, hdy=3),
    KJ(5.25, dict(SITJ, uaL=-70, faL=-110, uaR=70, faR=110), eyes="wide", mouth="o", hdx=0, hdy=-1),  # startled awake
    KJ(5.9, SITJ, eyes="left", hdy=0),
    KJ(6.7, SITJ, eyes="right", hdy=0),
    KJ(7.4, dict(SITJ, uaL=-165, faL=-178, uaR=150, faR=172), eyes="shut", mouth="yawn", hdy=-1),  # a big yawn and stretch
    KJ(8.8, dict(SITJ, uaL=-165, faL=-178, uaR=150, faR=172), eyes="shut", mouth="yawn", hdy=-1),
    KJ(9.6, SITJ, eyes="droop", hdy=0),
    KJ(10.8, SITJ, eyes="shut", hdx=1, hdy=1),
    KJ(12.0, SITJ, eyes="shut", hdx=1, hdy=1),
]


def scene_doze(c, t):
    tl = t % 12
    k = keyframe(DOZE, tl)
    k["shL"] += 8 * math.sin(t * 0.9)
    k["shR"] += 8 * math.sin(t * 0.9 + 2)
    hx, hy = 86, 60
    breath = fr(0.5 + 0.5 * math.sin(t * 1.6)) if k["eyes"] == "shut" and k["mouth"] == "pout" else 0
    draw_pierrot(c, hx, hy, k, eyes=k["eyes"], mouth=k["mouth"], hdx=fr(k["hdx"]), hdy=fr(k["hdy"]) + breath)
    if tl < 5.0 or tl >= 10.2:
        for n in range(2):
            u = (t * 0.35 + n / 2) % 1
            x, y = fr(hx + 6 + 8 * u + 2 * math.sin(t * 2 + n)), fr(hy - 27 - 14 * u)
            from stage import S as _S
            c.rect(x, y, 3, 1, alpha_over(c.px[y][x], FG, 1 - u))
            c.rect(x + 1, y + 1, 1, 1, alpha_over(c.px[y + 1][x + 1], FG, 1 - u))
            c.rect(x, y + 2, 3, 1, alpha_over(c.px[y + 2][x], FG, 1 - u))


# ---- sleep (last sliver): asleep on the crescent's horn, rocked by the moon, dreaming (8 s). ----
SLEEPJ = dict(uaL=-8, faL=-2, uaR=8, faR=2, thL=-82, shL=-4, thR=82, shR=4)
SLEEP = [
    KJ(0.0, SLEEPJ, eyes="shut", hdx=-1, hdy=2),
    KJ(3.0, SLEEPJ, eyes="shut", hdx=-1, hdy=2),
    KJ(4.0, SLEEPJ, eyes="shut", mouth="smile", hdx=-1, hdy=1),
    KJ(6.4, SLEEPJ, eyes="shut", mouth="smile", hdx=-1, hdy=1),
    KJ(7.2, SLEEPJ, eyes="shut", hdx=-1, hdy=2),
    KJ(8.0, SLEEPJ, eyes="shut", hdx=-1, hdy=2),
]
ZZ = ["yyy", "..y", ".y.", "y..", "yyy"]


def scene_sleep(c, t, mx=110, my=46):
    tl = t % 8
    k = keyframe(SLEEP, tl)
    rock = fr(math.sin(t * 0.8))
    k["shL"] += 6 * math.sin(t * 0.7)
    k["shR"] += 6 * math.sin(t * 0.7 + 1.5)
    hx, hy = mx - 7, my - 18 + rock
    breath = fr(0.5 + 0.5 * math.sin(t * 1.3))
    draw_pierrot(c, hx, hy, k, eyes="shut", mouth=k["mouth"], hdx=-1, hdy=fr(k["hdy"]) + breath, blush=k["mouth"] == "smile")
    for n in range(3):
        u = (t * 0.28 + n / 3) % 1
        x, y = fr(hx + 4 + 12 * u + 2 * math.sin(t * 2 + n)), fr(hy - 26 - 16 * u)
        if y >= 0:
            c.sprite(ZZ, x, y, {"y": alpha_over(c.px[y][x], FG, 1 - u)})
    # The dream: bubbles drift up beside his head to a little full moon, while he smiles.
    if 3.6 <= tl < 6.8:
        u = min(1, (tl - 3.6) / 0.6)
        for i, (bx, by, sz) in enumerate(((hx - 9, hy - 21, 1), (hx - 13, hy - 23, 2))):
            if u > i * 0.45:
                c.rect(bx, by, sz, sz, FG, 0.55)
        if u >= 1:
            cx, cy = hx - 22, hy - 25
            for dy in range(-4, 5):
                hw = math.floor(math.sqrt(20 - dy * dy))
                c.rect(cx - hw, cy + dy, 2 * hw + 1, 1, FG, 0.16)
            for dy in range(-2, 3):
                hw = math.floor(math.sqrt(6 - dy * dy))
                c.rect(cx - hw, cy + dy, 2 * hw + 1, 1, mix(PAL["yellow"], FG, 0.6))
