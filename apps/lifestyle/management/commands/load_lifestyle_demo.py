"""Seed the Lifestyle magazine: 6 categories, 3 authors, ~12 articles.

Every post_type and template state is represented so the magazine is fully
demonstrable. Hero images are generated placeholders (category-coloured banners).
Idempotent-ish: skips if articles already exist (delete them to reseed).

    python manage.py load_lifestyle_demo
"""
import datetime
import random
from io import BytesIO

from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from PIL import Image, ImageDraw, ImageFont
from wagtail.images import get_image_model

from apps.lifestyle.models import (
    ArticleGalleryImage, ArticlePage, ArticleProduct, AuthorIndexPage, AuthorPage,
    CategoryPage, LifestyleIndexPage,
)

WagtailImage = get_image_model()

AUTHORS = [
    ("Eleanor Voss", "Editor-at-Large · Horology",
     "Two decades covering watch auctions, independent makers and the trade."),
    ("Marcus Hale", "Motorsport Correspondent",
     "Paddock reporter across Formula 1 and endurance racing."),
    ("Sofia Marchetti", "Sailing & Travel Editor",
     "Bluewater sailor and luxury-travel writer, at home on any dock."),
]

CATEGORIES = [
    ("Fashion", "fashion", (61, 42, 32)),
    ("Motorsports", "motorsports", (120, 40, 36)),
    ("Watersports", "watersports", (30, 74, 110)),
    ("Business", "business", (40, 58, 45)),
    ("Entertainment", "entertainment", (90, 45, 90)),
    ("Health", "health", (30, 90, 70)),
]

# (cat_slug, title, dek, post_type, [tags], author_idx, days_ago, sponsored)
ARTICLES = [
    ("motorsports", "On the Grid: The Watches of the Modern F1 Paddock", "How racing drivers pick their wrist companions.", "feature", ["f1", "watches", "chronograph"], 1, 2, False),
    ("motorsports", "Le Mans at Dawn: A Photo Essay", "Twenty-four hours through the lens.", "gallery", ["le mans", "endurance"], 1, 9, False),
    ("watersports", "A Collector's Guide to Regatta Season", "What to pack, wear and wind.", "guide", ["sailing", "regatta"], 2, 4, False),
    ("watersports", "Crossing the Atlantic by Sail", "One writer's two-week passage.", "feature", ["sailing", "travel"], 2, 14, False),
    ("fashion", "Ten Watches That Belong on a Bridge Deck", "Our editors' picks for life afloat.", "list", ["watches", "style"], 0, 1, False),
    ("fashion", "The Quiet Luxury of the Racing Chronograph", "Why understatement always wins.", "standard", ["style", "chronograph"], 0, 7, False),
    ("business", "Inside the Boom in Independent Watchmaking", "The market's most interesting corner.", "standard", ["market", "independents"], 0, 3, False),
    ("business", "Auction Report: A Record Season", "What sold, and what it means.", "review", ["auction", "market"], 0, 11, False),
    ("entertainment", "A Weekend at Goodwood", "Cars, cocktails and the crowd.", "event", ["goodwood", "event"], 1, 5, True),
    ("entertainment", "The Directors Who Collect", "Hollywood's quiet horology habit.", "interview", ["culture", "watches"], 0, 16, False),
    ("health", "The Sailor's Guide to Sea-Legs and Sleep", "Staying sharp on a long passage.", "guide", ["wellness", "sailing"], 2, 6, False),
    ("health", "Grip, Grit and the Racing Driver's Body", "The fitness behind the wheel.", "standard", ["fitness", "motorsport"], 1, 13, False),
    # Media variants (iNews video / audio / quote templates)
    ("motorsports", "In Conversation: A Team Principal on the Season Ahead", "Twelve minutes in the paddock.", "video", ["f1", "interview"], 1, 8, False),
    ("entertainment", "The Pier & Paddock Podcast, Episode One", "The harbor and the grid, in your ears.", "audio", ["podcast", "culture"], 0, 10, False),
    ("business", "“Buy the seller, not the watch”", "A veteran dealer's rule for a nervous market.", "quote", ["watches", "market"], 0, 12, False),
]

YOUTUBE_EMBED = "https://www.youtube.com/embed/2Gg6Seob5Mg"
SOUNDCLOUD_EMBED = ("https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/"
                    "tracks/51057943&color=%239A7B43&auto_play=false&show_user=true")

BODY = [
    "<p>There is a particular pleasure in the details — the click of a bezel, the "
    "snap of a mainsheet, the shift into a higher gear. This is a story about people "
    "who notice those things, and the objects they choose to live with.</p>",
    "<p>We spent time with collectors, makers and the merely obsessed to understand "
    "what draws the affluent enthusiast to the harbor and the grid. The answer, as "
    "ever, is less about price than provenance — and the quiet confidence of getting "
    "it right.</p>",
    "<p>What follows is our field notes: unhurried, opinionated, and written for the "
    "reader who already knows the difference.</p>",
]


def _font(size):
    for path in ("/System/Library/Fonts/Supplemental/Georgia.ttf",
                 "/Library/Fonts/Georgia.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


class Command(BaseCommand):
    help = "Seed the Lifestyle magazine (categories, authors, articles)."

    def handle(self, *args, **options):
        random.seed(77)
        index = LifestyleIndexPage.objects.first()
        if index is None:
            self.stderr.write("Run `lifestyle_bootstrap` first."); return
        if ArticlePage.objects.exists():
            self.stdout.write("Articles already exist — delete them to reseed."); return

        # Authors
        author_index = AuthorIndexPage.objects.first()
        if author_index is None:
            author_index = AuthorIndexPage(title="Authors", slug="authors",
                                           intro="The bylines behind Pier & Paddock Lifestyle.")
            index.add_child(instance=author_index)
            author_index.save_revision().publish()
        authors = []
        for name, role, bio in AUTHORS:
            a = AuthorPage(title=name, slug=slugify(name), role=role,
                           bio="<p>%s</p>" % bio,
                           portrait=self._image(name, name.split()[0], 400, 400,
                                                (27, 42, 65)))
            author_index.add_child(instance=a)
            a.save_revision().publish()
            authors.append(a)
        self.stdout.write("  authors: %d" % len(authors))

        # Categories
        cats = {}
        for title, slug, color in CATEGORIES:
            c = CategoryPage(
                title=title, slug=slug,
                intro="<p>Our %s desk covers the people, places and objects that "
                      "define life at the harbor and the grid — reported with the "
                      "eye of an insider and the standards of a collector.</p>" % title.lower(),
                accent_color="#9A7B43",
                hero_image=self._image("%s hero" % title, title, 1200, 500, color))
            index.add_child(instance=c)
            c.save_revision().publish()
            cats[slug] = (c, color)
        self.stdout.write("  categories: %d" % len(cats))

        # Products for shoppable cards
        from oscar.core.loading import get_model
        Product = get_model("catalogue", "Product")
        products = list(Product.objects.browsable()[:40])
        now = timezone.now()

        made = 0
        for slug, title, dek, ptype, tags, aidx, days_ago, sponsored in ARTICLES:
            cat, color = cats[slug]
            dt = now - datetime.timedelta(days=days_ago, hours=random.randint(0, 12))
            art = ArticlePage(
                title=title, slug=slugify(title)[:60],
                subtitle=dek, post_type=ptype, is_sponsored=sponsored,
                hero_image=self._image(title, cat.title, 1200, 700, color),
                hero_alt_text="%s — %s" % (title, cat.title),
                hero_credit="Pier & Paddock",
                publish_display_date=dt.date(),
                body=self._rich_body(random.choice(products).id if products else None),
                lead_video_url=YOUTUBE_EMBED if ptype == "video" else "",
                lead_audio_url=SOUNDCLOUD_EMBED if ptype == "audio" else "",
            )
            cat.add_child(instance=art)
            art.authors.set([authors[aidx]])
            for t in tags:
                art.tags.add(t)
            if ptype == "gallery":
                for i in range(4):
                    art.gallery_images.add(ArticleGalleryImage(
                        image=self._image("%s frame %d" % (title, i + 1), cat.title, 1000, 620, color),
                        caption="%s — frame %d" % (cat.title, i + 1)))
            # Shoppable products on watch-tagged stories
            if "watches" in tags or "chronograph" in tags:
                for p in random.sample(products, 3):
                    art.related_products.add(ArticleProduct(product=p))
            art.first_published_at = dt
            art.save()
            art.save_revision().publish()
            made += 1
        self.stdout.write(self.style.SUCCESS("  articles: %d" % made))

        # Curated sponsored product slots (article rail "Sponsored Products").
        from apps.lifestyle.models import SponsoredProductSlot
        SponsoredProductSlot.objects.all().delete()
        hooks = ["A bridge-deck classic.", "The paddock's quiet favourite.",
                 "Built for bluewater.", "An auction-room darling."]
        for i, p in enumerate(random.sample(products, min(4, len(products)))):
            SponsoredProductSlot.objects.create(
                product=p, hook=hooks[i % len(hooks)], advertiser="Pier & Paddock",
                sort_order=i)
        self.stdout.write("  sponsored slots: %d" % SponsoredProductSlot.objects.count())
        self.stdout.write(self.style.SUCCESS("Lifestyle demo seeded."))

    # -- helpers ----------------------------------------------------------
    def _rich_body(self, product_id):
        """A body that exercises the Phase 3 block set."""
        body = [
            ("paragraph", BODY[0]),
            ("key_takeaways", {"title": "Key takeaways", "points": [
                "The enthusiast market rewards provenance over price.",
                "Completeness — box, papers, history — is worth more than ever.",
                "Patience beats FOMO in a normalising market.",
            ]}),
            ("paragraph", BODY[1]),
            ("pull_quote", {"quote": "The people who get it right are rarely the ones "
                                     "shouting about it.",
                            "attribution": "A dealer, off the record"}),
            ("paragraph", BODY[2]),
        ]
        if product_id:
            body.append(("product", {"product_id": product_id,
                                     "blurb": "A fitting companion for the story above."}))
        body += [
            ("faq", {"items": [
                {"question": "Where do I start as a new collector?",
                 "answer": "<p>Buy the seller first: provenance, condition and a name you trust.</p>"},
                {"question": "Is now a good time to buy?",
                 "answer": "<p>For the patient, yes — the market has normalised from its peak.</p>"},
            ]}),
            ("divider", None),
            ("inline_ad", {"zone": "in_content"}),
        ]
        return body

    def _image(self, title, label, w, h, color):
        im = Image.new("RGB", (w, h), color)
        d = ImageDraw.Draw(im)
        # subtle darker footer band for legibility
        d.rectangle([0, h - int(h * 0.30), w, h], fill=tuple(int(c * 0.7) for c in color))
        font = _font(max(24, int(h * 0.085)))
        d.text((int(w * 0.05), h - int(h * 0.22)), label, fill=(255, 255, 255), font=font)
        d.rectangle([int(w * 0.05), h - int(h * 0.26), int(w * 0.05) + 90, h - int(h * 0.26) + 5],
                    fill=(154, 123, 67))
        bio = BytesIO()
        im.save(bio, "PNG")
        bio.seek(0)
        img = WagtailImage(title=title[:120],
                           file=ImageFile(bio, name=slugify(title)[:40] + ".png"),
                           width=w, height=h)
        img.save()
        return img
