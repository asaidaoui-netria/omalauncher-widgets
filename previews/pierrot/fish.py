"""Pierrot fishing from the crescent (the moon's "sit" phase): his line hangs in a lit dormer window; its light bites,
he reels it up as a star, admires it and tosses it into the sky, and the window comes back on. Mirrors the widget's OWL.

usage: fish.py   renders a contact sheet to out/fish/sheet.png
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sim import PAL, BG, FG, mix, alpha_over, draw_pierrot, seg_points, joint
from stage import keyframe, smooth, star_sprite, render, K, ROOF_PAL, STAR

WIN = (87, 61)  # the dormer window, as `fw` in the widget

# The same poses as before, looking down at the window while he waits.
FISH = [
    K(0.0, eyes="down", hdx=-1),
    K(2.6, eyes="down", hdx=-1),
    K(3.0, rod=-125, uaL=-30, eyes="wide", mouth="o", hdx=-1),                # a bite: the rod dips
    K(3.5, rod=-145, uaL=-55, faL=-140, eyes="wide", mouth="o"),              # strike: the light comes out
    K(5.4, rod=-150, uaL=-60, faL=-145, eyes="right", mouth="pout"),          # reeled in (cranking on top)
    K(5.8, rod=-150, uaL=-60, faL=-145, uaR=40, faR=-30, eyes="happy", mouth="smile"),
    K(6.9, rod=-150, uaL=-60, faL=-145, uaR=60, faR=20, eyes="happy", mouth="smile"),
    K(7.2, rod=-150, uaR=20, faR=-20, eyes="happy", mouth="smile"),
    K(7.6, rod=-140, uaR=150, faR=170, eyes="up", mouth="o"),                 # toss!
    K(8.4, rod=-130, uaR=60, faR=30, eyes="down", mouth="smile", hdx=-1),     # casts back down
    K(10.0, eyes="down", hdx=-1),
]


def attach(tl):
    """1 while the hook is in the window, 0 while it hangs at the rod: reeled up 3.5-5.4, cast down 8.4-9.6."""
    if tl < 3.5:
        return 1.0
    if tl < 5.4:
        return 1 - smooth((tl - 3.5) / 1.9)
    if tl < 8.4:
        return 0.0
    return smooth(min(1.0, (tl - 8.4) / 1.2))


def scene(c, t):
    tl = t % 10
    mx, my = 116, 47
    hx, hy = mx + 7, my - 18
    k = keyframe(FISH, tl)
    k["shL"] += 22 * math.sin(t * 2.1)
    k["shR"] += 22 * math.sin(t * 2.1 + 1.7)
    if 3.5 <= tl < 5.4:
        k["faR"] = -60 + 45 * math.sin(t * 11)
        k["uaR"] = 25 + 10 * math.sin(t * 11)
    if k["eyes"] in ("left", "down", "right") and t % 3.7 < 0.12:
        k["eyes"] = "shut"
    # The window: lit (the city draws it), flickering as the light bites, dark once it's caught, and back on
    # (with a flicker) after the hook is back.
    wx, wy = WIN
    # Its light spills around it while it's on, pulsing gently, flaring as it bites.
    if tl < 3.0 or tl >= 9.85:
        glow = 0.16 + 0.06 * math.sin(t * 2) if tl < 2.6 or tl >= 9.85 else 0.2 + 0.25 * (int(t * 16) % 2)
        c.rect(wx - 1, wy - 1, 3, 4, PAL["yellow"], a=glow)
        c.rect(wx, wy, 1, 2, mix(PAL["yellow"], FG, 0.25))
    if 2.6 <= tl < 3.0:
        if int(t * 16) % 2 == 0:
            c.rect(wx, wy, 1, 2, FG)
    elif 3.0 <= tl < 9.7:
        c.rect(wx, wy, 1, 2, ROOF_PAL["b"])
    elif 9.7 <= tl < 9.85:
        if int(t * 20) % 2 == 0:
            c.rect(wx, wy, 1, 2, ROOF_PAL["b"])
    draw_pierrot(c, hx, hy, k, eyes=k["eyes"], mouth=k["mouth"], hdx=round(k["hdx"]), hdy=round(k["hdy"]),
                 blush=k["mouth"] == "smile")
    sh = (hx - 6, hy - 10)
    el = joint(*sh, k["uaL"], 5)
    hand = joint(*el, k["faL"], 5)
    tip = joint(*hand, k["rod"], 16)
    for (x, y) in seg_points(*hand, *tip):
        c.rect(x, y, 1, 1, mix(PAL["orange"], BG, 0.35))
    # The line: from the tip to the hook, bowing a little in the breeze; the hook sits in the window, or hangs
    # 4 under the tip, or anywhere between while reeling and casting.
    a = attach(tl)
    hk = (round(tip[0] + (wx - tip[0]) * a), round(tip[1] + 4 + (wy - 1 - tip[1] - 4) * a))
    if 3.0 <= tl < 3.6:  # the strike: the line twitches
        hk = (hk[0] + round(math.sin(t * 25)), hk[1])
    sway = 1.5 * math.sin(t * 1.4)
    n = max(abs(hk[0] - tip[0]), abs(hk[1] - tip[1]), 1)
    for i in range(n):
        s = i / n
        c.rect(round(tip[0] + (hk[0] - tip[0]) * s + sway * math.sin(math.pi * s)), round(tip[1] + (hk[1] - tip[1]) * s),
               1, 1, alpha_over(c.px[0][0], FG, 0.55))
    c.rect(hk[0], hk[1], 1, 1, FG)
    c.rect(hk[0] + 1, hk[1] - 1, 1, 1, FG)
    # The light, caught: a small star on the hook that grows as it comes up, then in his hand, then thrown.
    if 3.0 <= tl < 5.8:
        big = tl >= 4.6
        star_sprite(c, hk[0], hk[1] + (2 if big else 1), STAR if big else mix(PAL["yellow"], FG, 0.25), big=big)
    elif 5.8 <= tl < 7.6:
        rh = joint(*joint(hx + 6, hy - 10, k["uaR"], 5), k["faR"], 5)
        star_sprite(c, rh[0], rh[1] - 3, STAR, big=True)
        if int(t * 6) % 2 == 0:
            c.rect(rh[0] + 3, rh[1] - 6, 1, 1, FG)
    elif 7.6 <= tl < 9.0:
        u = (tl - 7.6) / 1.4
        sx = hx + 10 - 70 * u
        sy = hy - 18 - 22 * math.sin(u * math.pi * 0.5) + 10 * u * u
        star_sprite(c, sx, max(sy, 3), STAR, big=u < 0.5)
    elif tl >= 9.0:
        star_sprite(c, 46, 6, alpha_over(c.px[6][46], STAR, 0.5 + 0.5 * abs(math.sin(t * 4))))


if __name__ == "__main__":
    from PIL import Image
    os.makedirs("out/fish", exist_ok=True)
    times = [0.5, 2.8, 3.2, 4.2, 5.0, 6.2, 7.9, 8.8, 9.2, 9.9]
    ims = []
    for tm in times:
        p = "out/fish/f%05.2f.png" % tm
        render(tm, scene=scene).save(p, 3)
        ims.append(Image.open(p))
    w, h = ims[0].size
    sheet = Image.new("RGB", (w * 2 + 6, (h + 6) * 5), (20, 20, 30))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % 2) * (w + 6), (i // 2) * (h + 6)))
    sheet.save("out/fish/sheet.png")
    print("ok")
