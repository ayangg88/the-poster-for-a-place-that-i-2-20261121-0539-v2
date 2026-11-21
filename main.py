#!/usr/bin/env python3
"""VELMARA — Where the Sea Falls Up.

A travel poster for a place that does not exist: floating isles above a
dusk sea, where the waterfalls flow UP from the sea to the islands.

Deterministic, Pillow only, no network. Writes /output/entry.png (1024x1024).
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
OUT = "/output/entry.png"
SEED = 20261121

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

CREAM = (252, 240, 214)
WARM = (255, 214, 150)
RIM = (255, 196, 120)
LAVENDER = (216, 210, 232)
SHADOW = (18, 12, 40)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def gradient(draw, y0, y1, c0, c1):
    """Fill rows y0..y1 with a vertical gradient from c0 to c1."""
    span = max(1, y1 - y0)
    for y in range(y0, y1 + 1):
        draw.line([(0, y), (W - 1, y)], fill=lerp(c0, c1, (y - y0) / span))


def tracked_size(font, text, tracking):
    total = 0
    for ch in text:
        total += draw_text_width(font, ch) + tracking
    return total - tracking


def draw_text_width(font, text):
    left, top, right, bottom = font.getbbox(text)
    return right - left


def draw_tracked(draw, cx, y, text, font, fill, tracking, shadow=None):
    """Draw letter-tracked text centred on cx, top at y."""
    widths = [draw_text_width(font, ch) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        if shadow is not None:
            draw.text((x + 3, y + 3), ch, font=font, fill=shadow)
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + tracking


def main():
    rng = random.Random(SEED)
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)

    # ---- Sky: dusk gradient down to the horizon (~y700) ----
    gradient(d, 0, 250, (16, 14, 48), (44, 34, 92))
    gradient(d, 250, 450, (44, 34, 92), (96, 58, 122))
    gradient(d, 450, 600, (96, 58, 122), (214, 110, 96))
    gradient(d, 600, 700, (214, 110, 96), (250, 178, 110))

    # ---- Stars in the upper sky ----
    for _ in range(140):
        x = rng.randint(36, W - 36)
        y = rng.randint(36, 430)
        r = rng.choice([1, 1, 1, 2])
        a = rng.randint(90, 235)
        d.ellipse([x - r, y - r, x + r, y + r],
                  fill=(a, a, min(255, a + 20)))
    # 8 brighter cross-sparkle stars
    for _ in range(8):
        x = rng.randint(80, W - 80)
        y = rng.randint(50, 380)
        arm = rng.randint(5, 9)
        col = (235, 235, 255)
        d.line([(x - arm, y), (x + arm, y)], fill=col, width=1)
        d.line([(x, y - arm), (x, y + arm)], fill=col, width=1)
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=col)

    # ---- Low sun: soft glow, then disc, half-sunk at the horizon ----
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for r in range(320, 0, -4):
        alpha = int(70 * (1 - r / 320) ** 1.6)
        gd.ellipse([512 - r, 640 - r, 512 + r, 640 + r],
                   fill=(255, 166, 88, alpha))
    img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([512 - 92, 640 - 92, 512 + 92, 640 + 92], fill=(255, 214, 150))
    d.ellipse([512 - 66, 640 - 66, 512 + 66, 640 + 66], fill=(255, 228, 178))

    # ---- Horizon ridge silhouette ----
    ridge = []
    for x in range(0, W + 9, 8):
        y = 700 + 6 * math.sin(x / 170.0) + 3 * math.sin(x / 61.0 + 1.3)
        ridge.append((x, y))
    ridge += [(W, H), (0, H)]
    d.polygon(ridge, fill=(52, 40, 88))

    # ---- Sea: gradient below the horizon ----
    gradient(d, 700, 850, (58, 44, 96), (34, 52, 96))
    gradient(d, 850, H, (34, 52, 96), (14, 20, 52))

    # ---- Sun path: warm strokes on the water, narrowing with depth ----
    path = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(path)
    for i in range(15):
        y = 712 + i * 12
        t = i / 14.0
        half = int(150 * (1 - t * 0.85))
        alpha = int(150 * (1 - t * 0.7))
        pd.line([(512 - half, y), (512 + half, y)],
                fill=(255, 190, 120, alpha), width=5)
    img.paste(Image.alpha_composite(img.convert("RGBA"), path).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)

    # ---- Faint wave strokes (kept clear of the footer text) ----
    waves = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(waves)
    for _ in range(70):
        x = rng.randint(40, W - 90)
        y = rng.randint(730, 895)
        ln = rng.randint(18, 60)
        wd.line([(x, y), (x + ln, y)], fill=(140, 160, 210, 70), width=2)
    img.paste(Image.alpha_composite(img.convert("RGBA"), waves).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)

    # ---- Upward waterfalls: sea jets rising to strike the isles ----
    jets = [
        # (sea_x, island underside target x, y)
        (300, 300, 530),
        (730, 730, 470),
        (880, 880, 600),
        (130, 130, 616),
    ]
    jet_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    jd = ImageDraw.Draw(jet_layer)
    for sx, tx, ty in jets:
        # S-curve control points from the sea (y700) up to the rock
        pts = []
        for i in range(21):
            t = i / 20.0
            x = sx + (tx - sx) * t + 26 * math.sin(t * math.pi * 1.15) * (1 if sx < 512 else -1)
            y = 700 + (ty - 700) * t
            pts.append((x, y))
        # Rising-jet taper: WIDE at the sea launch, NARROW at the top,
        # like a fountain geyser — the opposite silhouette of a waterfall.
        for (w0, w1, alpha) in ((17, 5, 90), (11, 3, 150), (6, 2, 230)):
            for i in range(20):
                t = i / 20.0
                w = max(2, int(round(w0 + (w1 - w0) * t)))
                jd.line([pts[i], pts[i + 1]],
                        fill=(190, 225, 255, alpha), width=w, joint="curve")
        # droplets climbing the jet, shrinking toward the top
        for i in range(6):
            t = 0.12 + i * 0.15
            x = sx + (tx - sx) * t + 26 * math.sin(t * math.pi * 1.15) * (1 if sx < 512 else -1)
            y = 700 + (ty - 700) * t
            r = max(2, int(7 - i))
            jd.ellipse([x - r, y - r, x + r, y + r], fill=(210, 235, 255, 220))
        # erupting launch plume at the sea: a bright mound of water
        # bursting UPWARD where the jet leaves the sea
        jd.ellipse([sx - 24, 700 - 16, sx + 24, 700 + 4],
                   fill=(225, 242, 255, 235))
        jd.ellipse([sx - 12, 700 - 26, sx + 12, 700 + 2],
                   fill=(240, 248, 255, 235))
        for k, rr in enumerate((34, 26, 18)):
            jd.ellipse([sx - rr, 700 - 6, sx + rr, 700 + 6],
                       outline=(200, 230, 255, 200 - k * 50), width=2)
    img.paste(Image.alpha_composite(img.convert("RGBA"), jet_layer).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)

    # ---- Floating islands ----
    islands = [
        (300, 470, 250, 120),
        (730, 400, 300, 140),
        (512, 300, 190, 95),
        (880, 560, 170, 80),
        (130, 580, 150, 72),
    ]
    for cx, cy, w, h in islands:
        # rock underside: tapered body down to a point
        rock = [(cx - w / 2, cy), (cx + w / 2, cy),
                (cx + w * 0.18, cy + h * 0.95), (cx, cy + h * 1.25),
                (cx - w * 0.18, cy + h * 0.95)]
        d.polygon(rock, fill=(38, 30, 62))
        # grassy cap: flattened ellipse top
        d.ellipse([cx - w / 2, cy - h * 0.42, cx + w / 2, cy + h * 0.28],
                  fill=(46, 122, 74))
        d.ellipse([cx - w / 2, cy - h * 0.42, cx + w / 2, cy - h * 0.05],
                  fill=(58, 140, 88))
        # warm rim light along the cap's upper edge
        d.arc([cx - w / 2, cy - h * 0.42, cx + w / 2, cy + h * 0.28],
              start=180, end=360, fill=RIM, width=4)
        # lantern tree: thin trunk, dark-green blob, warm lantern dot
        tx = cx + rng.randint(-int(w * 0.2), int(w * 0.2))
        top_y = cy - h * 0.42
        d.line([(tx, top_y), (tx, top_y - 26)], fill=(30, 22, 48), width=3)
        d.ellipse([tx - 13, top_y - 44, tx + 13, top_y - 20],
                  fill=(24, 74, 46))
        d.ellipse([tx - 3, top_y - 34, tx + 3, top_y - 28],
                  fill=(255, 205, 110))

    # ---- Impact spray: where each jet strikes its rock from below ----
    # (drawn AFTER the islands so the splash shows on the rock edge)
    def _inside(px, py, poly):
        inside = False
        n = len(poly)
        for i in range(n):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % n]
            if (y1 > py) != (y2 > py):
                xin = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
                if px < xin:
                    inside = not inside
        return inside

    spray = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(spray)
    pairs = [(islands[0], jets[0]), (islands[1], jets[1]),
             (islands[3], jets[2]), (islands[4], jets[3])]
    for (cx, cy, w, h), (sx, tx, ty) in pairs:
        rock = [(cx - w / 2, cy), (cx + w / 2, cy),
                (cx + w * 0.18, cy + h * 0.95), (cx, cy + h * 1.25),
                (cx - w * 0.18, cy + h * 0.95)]
        pts = []
        for i in range(21):
            t = i / 20.0
            x = sx + (tx - sx) * t + 26 * math.sin(t * math.pi * 1.15) * (1 if sx < 512 else -1)
            y = 700 + (ty - 700) * t
            pts.append((x, y))
        hit = pts[-1]
        for p in pts:  # first curve point, climbing from the sea, inside the rock
            if _inside(p[0], p[1], rock):
                hit = p
                break
        hx, hy = hit
        for ang in (-70, -45, -20, 5, 30, 55, 75):
            rad = math.radians(ang)
            ex = hx + 34 * math.sin(rad)
            ey = hy + 20 * abs(math.cos(rad)) + 6
            sd.line([(hx, hy + 2), (ex, ey)],
                    fill=(215, 238, 255, 220), width=3)
        for _ in range(16):
            ax = hx + rng.randint(-30, 30)
            ay = hy + rng.randint(0, 18)
            r = rng.randint(1, 3)
            sd.ellipse([ax - r, ay - r, ax + r, ay + r],
                       fill=(215, 238, 255, 210))
    img.paste(Image.alpha_composite(img.convert("RGBA"), spray).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)

    # ---- Gulls in the upper sky ----
    for _ in range(9):
        x = rng.randint(90, W - 90)
        y = rng.randint(300, 470)
        s = rng.randint(7, 12)
        d.arc([x - s, y - 4, x, y + 4], start=200, end=340, fill=(30, 24, 60), width=2)
        d.arc([x, y - 4, x + s, y + 4], start=200, end=340, fill=(30, 24, 60), width=2)

    # ---- Sailboat with lantern, and its reflection ----
    bx, by = 400, 838
    refl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(refl)
    for i in range(6):
        y = by + 26 + i * 5
        half = 34 - i * 4
        rd.line([(bx - half, y), (bx + half, y)],
                fill=(255, 200, 130, 90 - i * 12), width=3)
    img.paste(Image.alpha_composite(img.convert("RGBA"), refl).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)
    d.line([(bx, by - 62), (bx, by + 8)], fill=(22, 16, 44), width=3)
    d.polygon([(bx + 4, by - 58), (bx + 4, by - 6), (bx + 44, by - 6)],
              fill=(250, 240, 210))
    d.polygon([(bx - 4, by - 46), (bx - 4, by - 6), (bx - 34, by - 6)],
              fill=(238, 224, 190))
    d.polygon([(bx - 42, by + 6), (bx + 46, by + 6), (bx + 34, by + 22),
               (bx - 30, by + 22)], fill=(20, 16, 40))
    d.ellipse([bx - 3, by - 68, bx + 3, by - 62], fill=(255, 205, 110))

    # ---- Type ----
    title_font = ImageFont.truetype(SERIF_BOLD, 118)
    tag_font = ImageFont.truetype(SANS_BOLD, 30)
    foot_font = ImageFont.truetype(SANS, 24)
    small_font = ImageFont.truetype(SANS_BOLD, 17)
    draw_tracked(d, 512, 92, "VELMARA", title_font, CREAM, 14, shadow=SHADOW)
    draw_tracked(d, 512, 222, "WHERE THE SEA FALLS UP", tag_font, WARM, 10,
                 shadow=SHADOW)
    # thin warm rule with diamond ornaments
    d.line([(212, 268), (812, 268)], fill=WARM, width=2)
    for ox in (212, 812):
        d.polygon([(ox, 261), (ox + 6, 268), (ox, 275), (ox - 6, 268)],
                  fill=WARM)
    draw_tracked(d, 512, 920, "VISIT THE ISLES BEYOND THE HORIZON",
                 foot_font, LAVENDER, 6, shadow=SHADOW)
    draw_tracked(d, 512, 954, "SAILINGS DAILY FROM THE EDGE OF THE MAP",
                 small_font, LAVENDER, 5, shadow=SHADOW)

    # ---- Double frame ----
    d.rectangle([18, 18, W - 19, H - 19], outline=CREAM, width=3)
    d.rectangle([30, 30, W - 31, H - 31], outline=CREAM, width=1)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, format="PNG", optimize=True)


if __name__ == "__main__":
    main()
