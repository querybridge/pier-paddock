"""Generate clean placeholder product imagery for the demo.

No real/copyrighted product photography is used. Each watch gets a few
consistent, stylised "angles" (front, dial close-up, caseback) drawn with
Pillow so the detail-page gallery, thumbnails and zoom all function.
"""
import io
import math

from PIL import Image, ImageDraw, ImageFont

CANVAS = 900

_FONT_CANDIDATES_SERIF = [
    "/System/Library/Fonts/Supplemental/Georgia.ttf",
    "/Library/Fonts/Georgia.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
]
_FONT_CANDIDATES_SANS = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def _font(paths, size):
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def serif(size):
    return _font(_FONT_CANDIDATES_SERIF, size)


def sans(size):
    return _font(_FONT_CANDIDATES_SANS, size)


# --- colour mapping -------------------------------------------------------
CASE_COLORS = {
    "steel": ((206, 210, 214), (150, 156, 162)),
    "stainless steel": ((206, 210, 214), (150, 156, 162)),
    "two-tone": ((216, 198, 140), (170, 150, 96)),
    "yellow gold": ((222, 188, 104), (176, 142, 64)),
    "rose gold": ((222, 170, 132), (178, 124, 92)),
    "white gold": ((226, 228, 230), (180, 184, 188)),
    "platinum": ((226, 228, 230), (180, 184, 188)),
    "titanium": ((150, 154, 158), (110, 114, 118)),
    "ceramic": ((46, 46, 48), (26, 26, 28)),
}

DIAL_COLORS = {
    "black": (24, 24, 26),
    "white": (240, 240, 238),
    "silver": (210, 212, 214),
    "blue": (32, 58, 104),
    "green": (28, 74, 52),
    "slate": (70, 78, 86),
    "grey": (96, 100, 104),
    "gray": (96, 100, 104),
    "champagne": (224, 200, 150),
    "salmon": (224, 158, 132),
    "brown": (78, 54, 38),
    "rose": (210, 150, 140),
    "ice blue": (180, 210, 222),
    "meteorite": (96, 96, 104),
}


def _case_color(material):
    key = (material or "steel").strip().lower()
    for name, cols in CASE_COLORS.items():
        if name in key:
            return cols
    return CASE_COLORS["steel"]


def _dial_color(dial):
    key = (dial or "black").strip().lower()
    for name, col in DIAL_COLORS.items():
        if name in key:
            return col
    return DIAL_COLORS["black"]


def _vertical_gradient(top, bottom):
    base = Image.new("RGB", (CANVAS, CANVAS), top)
    draw = ImageDraw.Draw(base)
    for y in range(CANVAS):
        t = y / CANVAS
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        draw.line([(0, y), (CANVAS, y)], fill=(r, g, b))
    return base


def _text_centered(draw, cx, y, text, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text((cx - w / 2, y), text, font=font, fill=fill)


def _draw_hand(draw, cx, cy, angle_deg, length, width, fill):
    a = math.radians(angle_deg - 90)
    x = cx + length * math.cos(a)
    y = cy + length * math.sin(a)
    draw.line([(cx, cy), (x, y)], fill=fill, width=width)


def _draw_watch(draw, cx, cy, radius, case_cols, dial_col, with_strap,
                strap_col, brand, model):
    light = dial_col if sum(dial_col) > 380 else (235, 235, 233)
    # Strap — drawn as short lug stubs so it never collides (dark-on-dark)
    # with the brand caption at the top or the model/ref caption at the bottom.
    if with_strap:
        sw = int(radius * 0.62)
        top_end = cy - radius - 95
        bot_end = cy + radius + 95
        draw.polygon(
            [(cx - sw, cy - radius), (cx + sw, cy - radius),
             (cx + sw * 0.85, top_end), (cx - sw * 0.85, top_end)],
            fill=strap_col,
        )
        draw.polygon(
            [(cx - sw, cy + radius), (cx + sw, cy + radius),
             (cx + sw * 0.85, bot_end), (cx - sw * 0.85, bot_end)],
            fill=strap_col,
        )
    # Outer case
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                 fill=case_cols[1])
    r2 = int(radius * 0.94)
    draw.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=case_cols[0])
    # Bezel
    rb = int(radius * 0.82)
    draw.ellipse([cx - rb, cy - rb, cx + rb, cy + rb], fill=case_cols[1])
    # Dial
    rd = int(radius * 0.72)
    draw.ellipse([cx - rd, cy - rd, cx + rd, cy + rd], fill=dial_col)
    # Crown
    draw.rectangle([cx + radius - 4, cy - 16, cx + radius + 18, cy + 16],
                   fill=case_cols[1])
    # Hour markers
    for i in range(12):
        a = math.radians(i * 30)
        x1 = cx + (rd - 14) * math.cos(a)
        y1 = cy + (rd - 14) * math.sin(a)
        x2 = cx + (rd - 36) * math.cos(a)
        y2 = cy + (rd - 36) * math.sin(a)
        draw.line([(x1, y1), (x2, y2)], fill=light, width=7)
    # Brand + model on dial
    if brand:
        _text_centered(draw, cx, cy - rd * 0.42, brand.upper(),
                       sans(int(rd * 0.13)), light)
    if model:
        _text_centered(draw, cx, cy + rd * 0.30, model.upper(),
                       sans(int(rd * 0.085)), light)
    # Hands
    _draw_hand(draw, cx, cy, 300, rd * 0.5, 10, light)   # hour ~10:00
    _draw_hand(draw, cx, cy, 70, rd * 0.72, 7, light)    # minute
    _draw_hand(draw, cx, cy, 160, rd * 0.78, 3, (198, 164, 77))  # seconds (gold)
    draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(198, 164, 77))


def _caseback(draw, cx, cy, radius, case_cols, brand, ref, year):
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                 fill=case_cols[1])
    r2 = int(radius * 0.9)
    draw.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=case_cols[0])
    r3 = int(radius * 0.66)
    draw.ellipse([cx - r3, cy - r3, cx + r3, cy + r3], outline=case_cols[1],
                 width=6)
    ink = (90, 84, 74)
    _text_centered(draw, cx, cy - 60, brand.upper(), serif(46), ink)
    _text_centered(draw, cx, cy - 4, ref, sans(30), ink)
    _text_centered(draw, cx, cy + 40, "SAPPHIRE CRYSTAL", sans(22), ink)
    if year:
        _text_centered(draw, cx, cy + 76, str(year), sans(22), ink)


def render(brand, model, ref, material, dial, angle, year=None):
    """Return PNG bytes for one product image.

    angle: 0 = front (with strap), 1 = dial close-up, 2 = caseback.
    """
    img = _vertical_gradient((247, 244, 239), (228, 222, 211))
    draw = ImageDraw.Draw(img)
    case_cols = _case_color(material)
    dial_col = _dial_color(dial)
    strap_col = (44, 40, 36) if "leather" not in (material or "").lower() else (70, 48, 34)
    cx = CANVAS // 2
    label = ""

    if angle == 2:
        _caseback(draw, cx, CANVAS // 2, 300, case_cols, brand, ref, year)
        label = "Caseback"
    elif angle == 1:
        _draw_watch(draw, cx, CANVAS // 2, 360, case_cols, dial_col,
                    False, strap_col, brand, model)
        label = "Dial Detail"
    else:
        _draw_watch(draw, cx, CANVAS // 2, 250, case_cols, dial_col,
                    True, strap_col, brand, model)
        label = "Front"

    # Header / footer captions
    _text_centered(draw, cx, 34, brand.upper(), serif(40), (40, 36, 30))
    foot = "%s · Ref. %s" % (model, ref)
    _text_centered(draw, cx, CANVAS - 70, foot, sans(26), (120, 112, 100))
    draw.text((36, CANVAS - 44), label, font=sans(20), fill=(170, 160, 145))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
