"""Compose final OG image: AI-generated background + crisp Hebrew typography overlay."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from bidi.algorithm import get_display

ROOT = Path(__file__).parent
SRC = ROOT / "Preview.png"
OUT = ROOT / "assets" / "og-image.png"

INK = (26, 26, 26)
PINK = (255, 79, 147)
W, H = 1200, 630


def rev(s: str) -> str:
    return get_display(s)


def fit_to(img: Image.Image, w: int, h: int) -> Image.Image:
    """Cover-fit: scale + center-crop to exact target size."""
    src_w, src_h = img.size
    scale = max(w / src_w, h / src_h)
    new_w = int(src_w * scale + 0.5)
    new_h = int(src_h * scale + 0.5)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    x = (new_w - w) // 2
    y = (new_h - h) // 2
    return img.crop((x, y, x + w, y + h))


def main():
    base = Image.open(SRC).convert("RGBA")
    base = fit_to(base, W, H)

    canvas = base.copy()
    d = ImageDraw.Draw(canvas)

    # Hebrew-capable bold fonts — Arial Bold renders Hebrew cleanly on Windows.
    title_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 130)
    sub_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 38)
    kicker_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 26)

    # Right edge anchor (RTL: text right-aligned to this x).
    right = W - 60

    # Pink kicker pill
    kicker = rev("קורס מקיף · 2026")
    kbox = d.textbbox((0, 0), kicker, font=kicker_font)
    kw, kh = kbox[2] - kbox[0], kbox[3] - kbox[1]
    pad_x, pad_y = 18, 10
    pill_x1 = right
    pill_x0 = right - kw - pad_x * 2
    pill_y0 = 80
    pill_y1 = pill_y0 + kh + pad_y * 2
    d.rounded_rectangle([pill_x0, pill_y0, pill_x1, pill_y1],
                        radius=24, fill=PINK, outline=INK, width=4)
    d.text((pill_x0 + pad_x, pill_y0 + pad_y - 4), kicker, font=kicker_font, fill=INK)

    # Two-line title — line spacing tighter than default
    line1 = rev("גיימינג")
    line2 = rev("בחינוך")
    y = pill_y1 + 30
    for line in (line1, line2):
        bbox = d.textbbox((0, 0), line, font=title_font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        # Soft shadow for pop
        d.text((right - tw + 5, y + 5), line, font=title_font, fill=(0, 0, 0, 60))
        d.text((right - tw, y), line, font=title_font, fill=INK)
        y += th + 10

    # Subtitle
    sub = rev("סילבוס הקורס · 29 מפגשים · 7 עולמות")
    sb = d.textbbox((0, 0), sub, font=sub_font)
    sw = sb[2] - sb[0]
    d.text((right - sw, y + 20), sub, font=sub_font, fill=INK)

    canvas.convert("RGB").save(OUT, quality=92, optimize=True)
    print("Wrote", OUT.name)


if __name__ == "__main__":
    main()
