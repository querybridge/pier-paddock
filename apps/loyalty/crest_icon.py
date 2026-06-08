"""Generate the Crest favicon (static/img/crest.ico).

Rasterises the same minimal monogram shield used on-page (black shield, muted
gold rule + "P&P" monogram) into a multi-size .ico for the browser tab. Run:

    python -m apps.loyalty.crest_icon

It's a build-time helper, not used at runtime — the committed crest.ico is what
the browser loads. Re-run it if the mark changes.
"""
import os

from PIL import Image, ImageDraw, ImageFont

BLACK = (13, 13, 13, 255)      # crest shield fill (matches CSS #0d0d0d)
GOLD = (154, 123, 67, 255)     # muted gold #9A7B43

# Shield outline in the SVG's 24x28 coordinate space (clockwise).
SHIELD = [
    (12, 1.2), (21.4, 4.1), (21.4, 13.5), (21.0, 16.0), (19.8, 18.8),
    (17.6, 21.6), (14.8, 24.2), (12, 26.8), (9.2, 24.2), (6.4, 21.6),
    (4.2, 18.8), (3.0, 16.0), (2.6, 13.5), (2.6, 4.1),
]
VBW, VBH = 24, 28


def _font(px):
    """Best-effort bold serif for the monogram; falls back to PIL default."""
    for path in (
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
        "/Library/Fonts/Georgia.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    ):
        try:
            return ImageFont.truetype(path, px)
        except OSError:
            continue
    return None


def _render(size, ss=4):
    """Render one square crest at `size`px (supersampled then downscaled)."""
    s = size * ss
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Fit the 24x28 shield into the square with a little padding.
    pad = s * 0.06
    scale = min((s - 2 * pad) / VBW, (s - 2 * pad) / VBH)
    ox = (s - VBW * scale) / 2
    oy = (s - VBH * scale) / 2

    def pt(x, y):
        return (ox + x * scale, oy + y * scale)

    d.polygon([pt(x, y) for x, y in SHIELD], fill=BLACK)
    # Fine gold rule.
    d.line([pt(6.8, 14.4), pt(17.2, 14.4)], fill=GOLD, width=max(1, int(scale * 0.9)))
    # Monogram — only legible (and only drawn) at larger sizes.
    if size >= 32:
        font = _font(int(scale * 6.4))
        if font is not None:
            cx, cy = pt(12, 9.2)
            d.text((cx, cy), "P&P", font=font, fill=GOLD, anchor="mm")

    return img.resize((size, size), Image.LANCZOS)


def build(out_path):
    sizes = [16, 32, 48, 64, 128, 256]
    frames = [_render(sz) for sz in sizes]
    base = frames[-1]
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    base.save(out_path, format="ICO", sizes=[(s, s) for s in sizes],
              append_images=frames[:-1])
    return out_path


if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    out = os.path.join(here, "static", "img", "crest.ico")
    print("wrote", build(out))
