"""Generate favicon (game controller) and OG preview image for Gaming Syllabus site."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from bidi.algorithm import get_display
import random

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
GAMES = ASSETS / "games"

CREAM = (253, 244, 227)
CREAM_SHADE = (245, 234, 208)
INK = (26, 26, 26)
PINK = (255, 79, 147)
YELLOW = (255, 210, 63)
MINT = (110, 231, 183)
LAVENDER = (167, 139, 250)
ORANGE = (251, 146, 60)
SKY = (56, 189, 248)


def rev(s: str) -> str:
    return get_display(s)


def make_favicon():
    size = 512
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Body of gamepad: rounded rect with two side bulges (like a SNES controller)
    cx, cy = size // 2, size // 2
    body_w, body_h = 420, 230
    body_x0 = cx - body_w // 2
    body_y0 = cy - body_h // 2
    body_x1 = cx + body_w // 2
    body_y1 = cy + body_h // 2

    outline = INK
    ow = 14

    # Left + right "ear" circles for the dual-grip silhouette
    ear_r = 130
    d.ellipse([body_x0 - 50, cy - ear_r, body_x0 - 50 + ear_r * 2, cy + ear_r], fill=PINK, outline=outline, width=ow)
    d.ellipse([body_x1 + 50 - ear_r * 2, cy - ear_r, body_x1 + 50, cy + ear_r], fill=PINK, outline=outline, width=ow)

    # Center body
    d.rounded_rectangle([body_x0, body_y0, body_x1, body_y1], radius=60, fill=PINK, outline=outline, width=ow)

    # D-pad (left) — black plus shape
    dp_cx = cx - 110
    dp_cy = cy - 10
    arm = 60
    thick = 26
    d.rectangle([dp_cx - arm, dp_cy - thick, dp_cx + arm, dp_cy + thick], fill=INK)
    d.rectangle([dp_cx - thick, dp_cy - arm, dp_cx + thick, dp_cy + arm], fill=INK)

    # Action buttons (right) — two circles
    btn_r = 30
    btn_cx = cx + 100
    btn_cy = cy - 10
    # Top button (yellow)
    d.ellipse([btn_cx + 20 - btn_r, btn_cy - 50 - btn_r, btn_cx + 20 + btn_r, btn_cy - 50 + btn_r],
              fill=YELLOW, outline=INK, width=8)
    # Right button (mint)
    d.ellipse([btn_cx + 70 - btn_r, btn_cy - btn_r, btn_cx + 70 + btn_r, btn_cy + btn_r],
              fill=MINT, outline=INK, width=8)
    # Bottom button (lavender)
    d.ellipse([btn_cx + 20 - btn_r, btn_cy + 50 - btn_r, btn_cx + 20 + btn_r, btn_cy + 50 + btn_r],
              fill=LAVENDER, outline=INK, width=8)
    # Left button (sky)
    d.ellipse([btn_cx - 30 - btn_r, btn_cy - btn_r, btn_cx - 30 + btn_r, btn_cy + btn_r],
              fill=SKY, outline=INK, width=8)

    # Start / Select pills (center top)
    pill_w, pill_h = 38, 12
    for offset in (-30, 30):
        d.rounded_rectangle([cx + offset - pill_w // 2, cy - 80 - pill_h // 2,
                             cx + offset + pill_w // 2, cy - 80 + pill_h // 2],
                            radius=6, fill=INK)

    img.save(ASSETS / "favicon.png")
    # Also save smaller sizes
    for s in (180, 64, 32, 16):
        resized = img.resize((s, s), Image.LANCZOS)
        resized.save(ASSETS / f"favicon-{s}.png")
    print("Wrote favicon.png + resized variants")


def add_halftone(img: Image.Image, opacity: int = 18, spacing: int = 22):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    r = 1
    for y in range(0, img.size[1], spacing):
        for x in range(0, img.size[0], spacing):
            od.ellipse([x - r, y - r, x + r, y + r], fill=(26, 26, 26, opacity))
    img.alpha_composite(overlay)


def paste_tilted(canvas, src_path, center, size, angle, border_color=INK, border_width=8):
    """Paste a square thumbnail tilted on canvas."""
    src = Image.open(src_path).convert("RGBA")
    # Center-crop to square
    w, h = src.size
    side = min(w, h)
    src = src.crop(((w - side) // 2, (h - side) // 2,
                    (w - side) // 2 + side, (h - side) // 2 + side))
    src = src.resize((size, size), Image.LANCZOS)

    # Build framed thumb on its own canvas
    frame = Image.new("RGBA", (size + 40, size + 40), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)
    # Drop shadow
    shadow = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rectangle([22, 22, size + 22, size + 22], fill=(0, 0, 0, 90))
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    frame.alpha_composite(shadow)
    # Border
    fd.rectangle([16, 16, size + 24, size + 24], fill=border_color)
    frame.paste(src, (20, 20))

    rotated = frame.rotate(angle, resample=Image.BICUBIC, expand=True)
    rx, ry = rotated.size
    canvas.alpha_composite(rotated, (center[0] - rx // 2, center[1] - ry // 2))


def make_og():
    W, H = 1200, 630
    img = Image.new("RGBA", (W, H), CREAM + (255,))
    add_halftone(img)
    d = ImageDraw.Draw(img)

    # ---------- Right-side thumbnail collage (RTL: visuals on the LEFT, text on the RIGHT) ----------
    # We'll place the visual cluster on the LEFT half of the canvas, text on the RIGHT half.
    games = [
        ("super-mario.png", -8, PINK),
        ("baba-is-you.png", 6, YELLOW),
        ("minecraft.jpg", -4, MINT),
        ("2048.jpg", 9, LAVENDER),
        ("pvz.jpg", -10, SKY),
        ("mini-metro-lesson.png", 5, ORANGE),
    ]
    # 3x2 layout on the left half
    cols = 3
    rows = 2
    thumb = 150
    gx0 = 70
    gy0 = 110
    gap = 30
    for i, (name, angle, color) in enumerate(games):
        path = GAMES / name
        if not path.exists():
            continue
        col = i % cols
        row = i // cols
        cx = gx0 + col * (thumb + gap) + thumb // 2
        cy = gy0 + row * (thumb + gap) + thumb // 2
        paste_tilted(img, path, (cx, cy), thumb, angle, border_color=color, border_width=8)

    # ---------- Decorative shapes ----------
    # Yellow burst star top-right
    star_cx, star_cy = W - 80, 70
    for r, c in [(58, YELLOW), (40, INK)]:
        pts = []
        import math
        for k in range(16):
            ang = math.pi * 2 * k / 16
            rr = r if k % 2 == 0 else r * 0.55
            pts.append((star_cx + math.cos(ang) * rr, star_cy + math.sin(ang) * rr))
        d.polygon(pts, fill=c)

    # Pink dot near title
    d.ellipse([W - 140, H - 110, W - 80, H - 50], fill=PINK, outline=INK, width=4)
    # Sky squiggle line under title (drawn as thick line)
    d.line([(W - 540, H - 95), (W - 200, H - 95)], fill=INK, width=6)
    d.line([(W - 540, H - 100), (W - 200, H - 100)], fill=SKY, width=10)

    # ---------- Title text (RTL) ----------
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 92)
        sub_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 34)
        kicker_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 24)
    except OSError:
        title_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
        kicker_font = ImageFont.load_default()

    text_right = W - 60
    # Kicker tag: pink pill
    kicker = rev("קורס מקיף · 2026")
    kw, kh = d.textbbox((0, 0), kicker, font=kicker_font)[2:]
    pill_pad = 14
    pill_x1 = text_right
    pill_x0 = text_right - kw - pill_pad * 2
    pill_y0 = 110
    pill_y1 = pill_y0 + kh + pill_pad
    d.rounded_rectangle([pill_x0, pill_y0, pill_x1, pill_y1], radius=20, fill=PINK, outline=INK, width=4)
    d.text((pill_x0 + pill_pad, pill_y0 + pill_pad // 2 - 2), kicker, font=kicker_font, fill=INK)

    # Main title — two lines, RTL aligned to right edge
    line1 = rev("גיימינג")
    line2 = rev("בחינוך")
    y = pill_y1 + 24
    for line in (line1, line2):
        bbox = d.textbbox((0, 0), line, font=title_font)
        tw = bbox[2] - bbox[0]
        # Shadow
        d.text((text_right - tw + 4, y + 4), line, font=title_font, fill=(0, 0, 0, 80))
        d.text((text_right - tw, y), line, font=title_font, fill=INK)
        y += bbox[3] - bbox[1] + 6

    # Subtitle
    sub = rev("סילבוס הקורס · 29 מפגשים · 7 עולמות")
    sb = d.textbbox((0, 0), sub, font=sub_font)
    sw = sb[2] - sb[0]
    d.text((text_right - sw, y + 18), sub, font=sub_font, fill=INK)

    img.convert("RGB").save(ASSETS / "og-image.png", quality=92, optimize=True)
    print("Wrote og-image.png")


if __name__ == "__main__":
    random.seed(7)
    make_favicon()
    make_og()
