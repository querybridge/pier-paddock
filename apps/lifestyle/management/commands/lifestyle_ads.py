"""Generate placeholder ad creatives + seed AdZone snippets (idempotent).

Inventoried from the iNews template (see LIFESTYLE_PROGRESS.md):
  leaderboard_top / in_content / footer — 730×95 (leaderboard, matches ads-long.jpg)
  sidebar                                — 350×350 (matches ads.jpg)

Each placeholder is a solid #666666 PNG with centered white "Your Ad Here",
written to static/lifestyle/img/placeholders/. Every zone links to /advertise/.
"""
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont

ZONES = [
    ("leaderboard_top", "Leaderboard (top)", 730, 95),
    ("in_content", "In-content leaderboard", 730, 95),
    ("footer", "Footer leaderboard", 730, 95),
    ("sidebar", "Sidebar rectangle", 350, 350),
]

GREY = (102, 102, 102)  # #666666
WHITE = (255, 255, 255)


def _font(size):
    for path in (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


class Command(BaseCommand):
    help = "Generate placeholder ad creatives + seed AdZone snippets."

    def handle(self, *args, **options):
        from apps.lifestyle.models import AdZone

        out_dir = os.path.join(
            settings.BASE_DIR, "apps", "lifestyle", "static", "lifestyle", "img", "placeholders"
        )
        os.makedirs(out_dir, exist_ok=True)

        for slug, name, w, h in ZONES:
            # Draw the placeholder (supersample ×2 for crisp text, then downscale).
            img = Image.new("RGB", (w * 2, h * 2), GREY)
            d = ImageDraw.Draw(img)
            font = _font(max(20, int(h * 2 * 0.28)))
            text = "Your Ad Here"
            box = d.textbbox((0, 0), text, font=font)
            tw, th = box[2] - box[0], box[3] - box[1]
            d.text(((w * 2 - tw) / 2 - box[0], (h * 2 - th) / 2 - box[1]),
                   text, fill=WHITE, font=font)
            d.rectangle([0, 0, w * 2 - 1, h * 2 - 1], outline=(120, 120, 120), width=2)
            img.resize((w, h), Image.LANCZOS).save(os.path.join(out_dir, "%s.png" % slug))

            AdZone.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name, "width": w, "height": h,
                    "target_url": "/advertise/",
                    "placeholder_image": "lifestyle/img/placeholders/%s.png" % slug,
                    "active": True,
                },
            )
            self.stdout.write("  %-16s %d×%d -> placeholder + AdZone" % (slug, w, h))

        self.stdout.write(self.style.SUCCESS("Ad zones ready (%d)." % len(ZONES)))
