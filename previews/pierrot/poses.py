"""Renders every pose at a few moments into one contact sheet: python poses.py [pose] [times...]."""
import math, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sim import Canvas, PAL, BG, FG, mix, alpha_over
import stage, scenes, fish

# montage needs a font for the labels: macOS's Helvetica, or ImageMagick's default elsewhere.
FONT = ["-font", "/System/Library/Fonts/Helvetica.ttc"] if os.path.exists("/System/Library/Fonts/Helvetica.ttc") else []

# pose: (moon centre, elongation to draw, scene)
POSES = {
    "seek": ((118, 30), 4, scenes.scene_seek),
    "sit": ((116, 47), 26, fish.scene),
    "play": ((120, 28), 110, scenes.scene_play),
    "serenade": ((118, 30), 180, scenes.scene_serenade),
    "doze": ((112, 41), 250, scenes.scene_doze),
    "sleep": ((110, 46), 322, scenes.scene_sleep),
}


def render(pose, t):
    (mx, my), el, scene = POSES[pose]
    if pose == "sleep":
        my += math.floor(math.sin(t * 0.8) + 0.5)
    c = Canvas(160, 72, stage.SKY[0])
    for b in range(4):
        c.rect(0, b * 14, 160, 14 if b < 3 else 30, stage.SKY[b])
    for n, (x, y) in enumerate(stage.STARS):
        c.rect(x, y, 1, 1, alpha_over(c.px[y][x], FG, 0.25 + 0.6 * abs(math.sin(t * 1.1 + n * 1.7))))
    if pose == "serenade":
        for r, a in ((25, 0.05), (22, 0.08)):
            for dy in range(-r, r + 1):
                hw = math.floor(math.sqrt(r * r - dy * dy))
                y = my + dy
                if 0 <= y < 72:
                    for x in range(max(0, mx - hw), min(160, mx + hw + 1)):
                        c.px[y][x] = alpha_over(c.px[y][x], PAL["yellow"], a + 0.03 * math.sin(t * 1.5))
    blush = pose == "serenade" and 10.2 <= t % 12 < 11.4
    pal = {"l": mix(PAL["yellow"], FG, 0.6) if not blush else mix(mix(PAL["yellow"], FG, 0.6), PAL["red"], 0.35),
           "m": mix(mix(PAL["yellow"], FG, 0.6), BG, 0.12)}
    for j, row in enumerate(stage.moon_rows(el)):
        for i, ch in enumerate(row):
            x, y = mx - 19 + i, my - 19 + j
            if 0 <= x < 160 and 0 <= y < 72:
                if ch in pal:
                    c.px[y][x] = pal[ch]
                elif ch == "d":
                    c.px[y][x] = alpha_over(c.px[y][x], FG, 0.1)
    stage.draw_city(c, t)
    scene(c, t)
    return c


if __name__ == "__main__":
    os.makedirs("out/poses", exist_ok=True)
    poses = [sys.argv[1]] if len(sys.argv) > 1 and sys.argv[1] in POSES else list(POSES)
    times = [float(a) for a in sys.argv[2:]] if len(sys.argv) > 2 else None
    for p in poses:
        ts = times or {"seek": [1, 5.8, 7.6, 9.2, 12], "sit": [1, 3.2, 6, 7.9], "play": [0.3, 2.1, 7.3, 7.7, 9],
                       "serenade": [1, 3, 5, 7.15, 9.4, 10.6], "doze": [2, 5.3, 6.2, 8, 11], "sleep": [1, 2.6, 4.8, 6.2]}[p]
        files = []
        for t in ts:
            f = "out/poses/%s_%05.2f.png" % (p, t)
            render(p, t).save(f, 3)
            files.append(f)
        subprocess.run(["montage"] + FONT + ["-label", "%t", "-pointsize", "12",
                        "-fill", "white"] + files + ["-tile", "2x", "-geometry", "+2+2", "-background", "#111",
                        "out/poses/sheet_%s.png" % p], check=True)
    print("ok")
