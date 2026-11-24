#!/usr/bin/env python3
"""Render the front page for Tuesday 24 November 2026.

Draws a newspaper front page (1024x1024) with a masthead, a globe with
numbered location pins, one lead story and eight further story panels.
All stories were verified against reputable sources on 24 Nov 2026.
Run: python3 render.py  -> writes entry.png next to this file.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
INK = (26, 26, 26)
PAPER = (246, 241, 227)
WHITE = (255, 255, 255)
RED = (176, 42, 48)
BLUE = (46, 111, 163)
BLUE_DK = (30, 80, 122)
LAND = (122, 154, 91)
GREY = (90, 86, 76)
RULE = (60, 58, 50)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, lines, fnt, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


# (number, category, place, headline, detail, extra, lon, lat, pin_dx, pin_dy)
STORIES = [
    ("1", "CONFLICT", "BENGHAZI, LIBYA",
     "Ukraine says it sank a Russian warship off Libya",
     "President Zelensky said naval drones sank the corvette Merkury at Benghazi port.",
     "The attack took place on Sunday; Kyiv confirmed it on Tuesday.",
     20.1, 32.1, -6, -16),
    ("2", "DIPLOMACY", "HONIARA",
     "Solomon Islands to drop China security pact",
     "Honiara told Beijing it will not renew the 2022 pact; a new treaty with Australia is expected.",
     "PM Matthew Wale meets Australia's Anthony Albanese on Wednesday.",
     160.0, -9.6, 0, 0),
    ("3", "BUSINESS", "PARIS",
     "Sanofi to buy Insmed for $41bn",
     "The French drugmaker agreed a $175-a-share cash deal, a 46% premium.",
     "Sanofi shares rose 5.6% on the news on Tuesday.",
     2.3, 48.9, -16, -10),
    ("4", "MARKETS", "NEW YORK",
     "Anthropic shares fall below IPO price",
     "The AI firm's stock slipped under its $83 debut price days after listing.",
     "CEO Dario Amodei sold shares worth over $280m a day after the debut.",
     -74.0, 40.7, 0, 0),
    ("5", "CONFLICT", "GAZA",
     "Israeli strikes kill at least six in Gaza",
     "Medics said two police officers were among the dead on Tuesday.",
     "Oxfam on Tuesday described Gaza as a 'toxic land'.",
     34.5, 31.5, -24, 18),
    ("6", "POLITICS", "BAGHDAD",
     "Iraq moves to take over Kurdish oilfields",
     "The PM ordered the oil ministry to manage fields in Kurdish-held areas.",
     "Baghdad also moved to take over border crossings in the region.",
     44.4, 33.3, 10, -20),
    ("7", "DISASTER", "NEPAL",
     "Magnitude 5.6 quake shakes eastern Nepal",
     "The tremor struck near the Tibet border; no casualties reported.",
     "Tremors were felt in India, Bhutan and Bangladesh.",
     87.9, 27.9, -14, 16),
    ("8", "SPACE", "CHINA",
     "Pakistan astronaut to join China's space station",
     "Zeeshan Ali is set to become the first foreign astronaut aboard Tiangong.",
     "He will fly on the Shenzhou-24 mission, the Straits Times reported.",
     105.0, 35.0, 18, 8),
    ("9", "DEFENCE", "BRUSSELS",
     "NATO vows to defend space after Russian reports",
     "Chief Mark Rutte spoke after reports Moscow may launch a nuclear-armed satellite.",
     "Rutte said the alliance will defend against any threats in space.",
     4.4, 50.8, 16, -14),
]


def project(cx, cy, r, lon, lat):
    """Equirectangular projection onto the globe disc, clamped inside it."""
    x = cx + r * (lon - 20.0) / 180.0
    y = cy - r * (lat - 25.0) / 90.0
    dx, dy = x - cx, y - cy
    d = (dx * dx + dy * dy) ** 0.5
    if d > r * 0.88:
        s = r * 0.88 / d
        x, y = cx + dx * s, cy + dy * s
    return x, y


def draw_globe(draw, cx, cy, r):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BLUE, outline=INK, width=3)
    # graticule
    for k in range(1, 4):
        yy = cy - r + 2 * r * k / 4
        half = (r * r - (yy - cy) ** 2) ** 0.5
        draw.line([cx - half, yy, cx + half, yy], fill=(120, 170, 205), width=1)
    for k in range(1, 4):
        xx = cx - r + 2 * r * k / 4
        half = (r * r - (xx - cx) ** 2) ** 0.5
        draw.line([xx, cy - half, xx, cy + half], fill=(120, 170, 205), width=1)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(120, 170, 205), width=1)
    # schematic landmasses (rough lon/lat polygons, same projection)
    land_polys = [
        # North America
        [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
         (-80, 62), (-75, 58), (-70, 44), (-75, 35), (-80, 32), (-85, 30),
         (-90, 29), (-97, 26), (-105, 23), (-110, 24), (-115, 29), (-120, 34),
         (-125, 40), (-125, 49), (-135, 58), (-150, 60), (-165, 60)],
        # South America
        [(-80, 10), (-75, 8), (-70, 11), (-62, 9), (-55, 6), (-50, 0),
         (-44, -3), (-38, -5), (-35, -9), (-40, -20), (-48, -28), (-55, -35),
         (-65, -41), (-68, -50), (-70, -54), (-73, -45), (-73, -30), (-70, -18),
         (-77, -12), (-80, -4)],
        # Africa
        [(-17, 15), (-15, 27), (-10, 31), (-5, 35), (10, 37), (20, 32),
         (32, 31), (35, 28), (38, 22), (43, 12), (48, 11), (51, 10),
         (46, 0), (40, -5), (40, -12), (35, -18), (32, -26), (28, -33),
         (20, -35), (16, -28), (12, -18), (12, -8), (9, 4), (-8, 5)],
        # Eurasia
        [(-10, 36), (-9, 43), (-2, 44), (0, 46), (3, 43), (8, 44), (12, 44),
         (18, 40), (22, 40), (26, 38), (30, 36), (36, 36), (36, 30), (43, 12),
         (50, 25), (57, 26), (61, 25), (66, 25), (70, 22), (76, 20), (80, 15),
         (80, 8), (88, 22), (92, 21), (97, 16), (100, 8), (104, 2), (104, 9),
         (109, 13), (109, 20), (114, 22), (120, 28), (122, 32), (126, 38),
         (130, 42), (135, 44), (140, 46), (142, 50), (142, 55), (150, 60),
         (158, 62), (162, 66), (170, 66), (178, 65), (180, 66), (170, 70),
         (160, 70), (140, 72), (120, 73), (100, 74), (80, 73), (60, 70),
         (50, 68), (40, 68), (32, 68), (30, 70), (25, 71), (18, 69), (12, 66),
         (10, 60), (5, 58), (5, 62), (10, 64), (15, 65), (18, 60), (21, 55),
         (24, 58), (28, 60), (30, 62), (28, 66), (25, 70), (18, 70), (12, 68),
         (5, 65), (-5, 60), (-10, 55), (-10, 50), (-5, 48), (-2, 44)],
        # Australia
        [(114, -22), (114, -30), (115, -35), (120, -34), (124, -33), (129, -32),
         (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
         (153, -32), (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
         (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
         (118, -20)],
    ]
    for poly in land_polys:
        pts = [project(cx, cy, r, lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=(90, 120, 70))
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=3)


def draw_pin(draw, x, y, num):
    draw.ellipse([x - 11, y - 11, x + 11, y + 11], fill=RED, outline=WHITE, width=2)
    f = font(SANS_B, 13)
    tw = draw.textlength(num, font=f)
    draw.text((x - tw / 2, y - 8), num, font=f, fill=WHITE)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # double border
    d.rectangle([8, 8, W - 9, H - 9], outline=INK, width=3)
    d.rectangle([16, 16, W - 17, H - 17], outline=INK, width=1)

    # ---- masthead ----
    y = 30
    d.text((W // 2, y), "ONE DAY  ·  NINE STORIES  ·  AROUND THE GLOBE",
           font=font(SANS_B, 17), fill=RED, anchor="ma")
    y = 56
    d.text((W // 2, y), "THE WORLD IN ONE DAY",
           font=font(SERIF, 58), fill=INK, anchor="ma")
    y = 122
    d.text((W // 2, y), "Tuesday 24 November 2026",
           font=font(SERIF, 34), fill=INK, anchor="ma")
    d.line([40, 168, W - 40, 168], fill=RULE, width=2)

    # ---- globe band ----
    gx, gy, gr = 175, 285, 105
    draw_globe(d, gx, gy, gr)
    for num, _cat, _pl, _h, _dt, _ex, lon, lat, pdx, pdy in STORIES:
        px, py = project(gx, gy, gr, lon, lat)
        draw_pin(d, px + pdx, py + pdy, num)
    d.text((gx, gy + gr + 12), "WHERE IT HAPPENED",
           font=font(SANS_B, 14), fill=GREY, anchor="ma")

    # ---- lead story (story 1) ----
    lx, ly, lw, lh = 310, 180, 674, 220
    d.rectangle([lx, ly, lx + lw, ly + lh], fill=WHITE, outline=INK, width=2)
    d.rectangle([lx, ly, lx + 46, ly + 46], fill=RED)
    d.text((lx + 23, ly + 7), "1", font=font(SANS_B, 30), fill=WHITE, anchor="ma")
    d.text((lx + 62, ly + 12), "CONFLICT  ·  BENGHAZI, LIBYA",
           font=font(SANS_B, 16), fill=RED)
    head = wrap(d, "Ukraine says it sank a Russian warship off Libya",
                font(SANS_B, 30), lw - 80)
    yy = text_block(d, lx + 62, ly + 44, head, font(SANS_B, 30), INK, 36)
    det = wrap(d, "President Zelensky said naval drones sank the corvette "
                  "Merkury at Benghazi port, taking the war far beyond the Black Sea. "
                  "The attack took place on Sunday; Kyiv confirmed it on Tuesday.",
               font(SANS, 18), lw - 80)
    text_block(d, lx + 62, yy + 8, det, font(SANS, 17), GREY, 23)

    # ---- story grid: stories 2..9, 4 cols x 2 rows ----
    cols, rows = 4, 2
    gx0, gy0 = 32, 424
    pw, ph, gap = 236, 272, 8
    f_cat = font(SANS_B, 13)
    f_head = font(SANS_B, 20)
    f_det = font(SANS, 15)
    f_loc = font(SANS_B, 12)
    for i, (num, cat, place, headline, detail, extra, _lon, _lat, _dx, _dy) in enumerate(STORIES[1:]):
        col, row = i % cols, i // cols
        x = gx0 + col * (pw + gap)
        yy0 = gy0 + row * (ph + gap)
        d.rectangle([x, yy0, x + pw, yy0 + ph], fill=WHITE, outline=INK, width=2)
        d.ellipse([x + 12, yy0 + 12, x + 38, yy0 + 38], fill=RED)
        fnum = font(SANS_B, 17)
        tw = d.textlength(num, font=fnum)
        d.text((x + 25 - tw / 2, yy0 + 16), num, font=fnum, fill=WHITE)
        d.text((x + 48, yy0 + 14), cat, font=f_cat, fill=RED)
        d.text((x + 48, yy0 + 32), place, font=f_loc, fill=GREY)
        head = wrap(d, headline, f_head, pw - 24)
        y2 = text_block(d, x + 12, yy0 + 58, head[:3], f_head, INK, 25)
        det = wrap(d, detail + " " + extra, f_det, pw - 24)
        text_block(d, x + 12, y2 + 8, det[:6], f_det, GREY, 20)

    # ---- footer ----
    fy = 988
    d.line([40, fy - 14, W - 40, fy - 14], fill=RULE, width=1)
    d.text((W // 2, fy), "Reported Tuesday 24 November 2026  ·  Sources: Reuters, BBC, Sydney Morning Herald, Xinhua",
           font=font(SANS, 13), fill=GREY, anchor="ma")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
