"""Load the reproducible demo catalogue.

    python manage.py load_demo_catalogue

Creates the Watch product class + attributes, brand/collection categories,
~50 fictional watches with generated placeholder imagery, stock records,
reviews on flagship pieces, a demo customer account, and blog posts.
"""
import datetime
import io
import shutil

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from oscar.apps.catalogue.categories import create_from_breadcrumbs
from oscar.core.loading import get_model

from apps.core import watch_images
from ._catalogue_data import BLOG_POSTS, BRANDS, COLLECTIONS, WATCHES

ProductClass = get_model("catalogue", "ProductClass")
Product = get_model("catalogue", "Product")
ProductAttribute = get_model("catalogue", "ProductAttribute")
ProductImage = get_model("catalogue", "ProductImage")
Category = get_model("catalogue", "Category")
ProductCategory = get_model("catalogue", "ProductCategory")
ProductReview = get_model("reviews", "ProductReview")
Partner = get_model("partner", "Partner")
StockRecord = get_model("partner", "StockRecord")

# code -> (display name, type)
ATTRIBUTES = [
    ("brand", "Brand", "text"),
    ("model", "Model", "text"),
    ("reference", "Reference Number", "text"),
    ("case_material", "Case Material", "text"),
    ("case_size", "Case Size", "text"),
    ("movement", "Movement", "text"),
    ("dial_color", "Dial Color", "text"),
    ("bracelet", "Bracelet / Strap", "text"),
    ("water_resistance", "Water Resistance", "text"),
    ("condition", "Condition", "text"),
    ("year", "Year", "integer"),
    ("box_papers", "Box & Papers", "text"),
]

ANGLE_LABELS = ["front", "dial", "caseback"]


class Command(BaseCommand):
    help = "Load the reproducible Pier & Paddock demo catalogue."

    def handle(self, *args, **options):
        self.stdout.write("Clearing previous demo data…")
        self._clear()

        self.stdout.write("Ensuring shipping countries…")
        self._ensure_countries()

        self.stdout.write("Creating product class and attributes…")
        product_class = self._create_product_class()

        self.stdout.write("Creating categories…")
        brand_cats, collection_cats = self._create_categories()

        partner, _ = Partner.objects.get_or_create(name="International Diamond Center")

        self.stdout.write("Creating %d watches with imagery…" % len(WATCHES))
        for data in WATCHES:
            self._create_watch(data, product_class, partner, brand_cats, collection_cats)

        self.stdout.write("Creating demo customer account…")
        self._create_demo_user()

        self.stdout.write("Seeding market values + vault holdings…")
        self._seed_vault()

        self.stdout.write("Creating blog posts…")
        self._create_blog_posts()

        n = Product.objects.count()
        sold = StockRecord.objects.filter(num_in_stock=0).count()
        self.stdout.write(self.style.SUCCESS(
            "Done. %d products (%d sold), %d reviews, %d blog posts."
            % (n, sold, ProductReview.objects.count(),
               _post_count())))

    # ------------------------------------------------------------------
    def _clear(self):
        ProductReview.objects.all().delete()
        ProductImage.objects.all().delete()
        StockRecord.objects.all().delete()
        Product.objects.all().delete()
        ProductCategory.objects.all().delete()
        Category.objects.all().delete()
        ProductClass.objects.filter(name="Watch").delete()
        try:
            from apps.blog.models import Post
            Post.objects.all().delete()
        except Exception:
            pass
        # Remove previous vault-save seed data (collector users + wishlists).
        try:
            from django.contrib.auth import get_user_model
            WishList = get_model("wishlists", "WishList")
            Line = get_model("wishlists", "Line")
            Line.objects.all().delete()
            WishList.objects.all().delete()
            get_user_model().objects.filter(email__startswith="collector").delete()
        except Exception:
            pass
        # Wipe generated media so re-runs start clean.
        from django.conf import settings
        for sub in ("images", "blog"):
            path = settings.MEDIA_ROOT / sub
            if path.exists():
                shutil.rmtree(path, ignore_errors=True)
        # Clear the sorl thumbnail cache too, so thumbnails regenerate from the
        # fresh source images. Otherwise stale cache entries (or ones recorded
        # while images were mid-deletion) can leave broken/blank thumbnails.
        try:
            from sorl.thumbnail.models import KVStore
            KVStore.objects.all().delete()
        except Exception:
            pass
        cache_dir = settings.MEDIA_ROOT / "cache"
        if cache_dir.exists():
            shutil.rmtree(cache_dir, ignore_errors=True)

    def _ensure_countries(self):
        """Checkout needs at least one shipping country."""
        Country = get_model("address", "Country")
        if Country.objects.count() == 0:
            from django.core.management import call_command
            try:
                call_command("oscar_populate_countries", "--initial-only")
            except Exception as exc:  # pragma: no cover - pycountry missing, etc.
                self.stdout.write(self.style.WARNING(
                    "  Could not auto-populate countries (%s). Run "
                    "'manage.py oscar_populate_countries' manually." % exc))
                return
        us = Country.objects.filter(iso_3166_1_a2="US").first()
        if us and not us.is_shipping_country:
            us.is_shipping_country = True
            us.save()

    def _create_product_class(self):
        pc = ProductClass.objects.create(
            name="Watch", requires_shipping=True, track_stock=True)
        for code, name, typ in ATTRIBUTES:
            ProductAttribute.objects.create(
                product_class=pc, name=name, code=code, type=typ, required=False)
        return pc

    def _create_categories(self):
        brand_cats, collection_cats = {}, {}
        for b in BRANDS:
            brand_cats[b] = create_from_breadcrumbs("Brands > %s" % b)
        for c in COLLECTIONS:
            collection_cats[c] = create_from_breadcrumbs("Collections > %s" % c)
        return brand_cats, collection_cats

    def _create_watch(self, d, product_class, partner, brand_cats, collection_cats):
        title = "%s %s" % (d["brand"], d["model"])
        product = Product.objects.create(
            product_class=product_class,
            structure=Product.STANDALONE,
            title=title,
            upc=slugify("%s-%s" % (d["brand"], d["ref"]))[:64],
            description=self._description(d),
            is_discountable=False,
        )
        # Attributes
        product.attr.brand = d["brand"]
        product.attr.model = d["model"]
        product.attr.reference = d["ref"]
        product.attr.case_material = d["material"]
        product.attr.case_size = d["size"]
        product.attr.movement = d["movement"]
        product.attr.dial_color = d["dial"]
        product.attr.bracelet = d["bracelet"]
        product.attr.water_resistance = d["water"]
        product.attr.condition = d["condition"]
        product.attr.year = int(d["year"])
        product.attr.box_papers = d["box_papers"]
        product.attr.save()

        # Categories: brand + each collection
        product.categories.add(brand_cats[d["brand"]])
        for c in d.get("collections", []):
            if c in collection_cats:
                product.categories.add(collection_cats[c])

        # Stock record
        from decimal import Decimal
        StockRecord.objects.create(
            product=product,
            partner=partner,
            partner_sku=d["ref"],
            price_currency="USD",
            price=Decimal(str(d["price"])),
            num_in_stock=int(d["stock"]),
        )

        # Images. A product may pin explicit photo files (relative to
        # static/assets/images/) — the first is the primary, the second is
        # the on-rollover secondary. Otherwise we generate front/dial/caseback.
        # Every product ends up with a primary AND a secondary image so the
        # grid rollover works everywhere.
        base = slugify(title)
        explicit = d.get("images")
        if explicit:
            from django.conf import settings
            img_root = settings.BASE_DIR / "static" / "assets" / "images"
            for i, rel in enumerate(explicit):
                src = img_root / rel
                with open(src, "rb") as fh:
                    data = fh.read()
                ext = src.suffix.lstrip(".") or "jpg"
                ProductImage.objects.create(
                    product=product,
                    original=ContentFile(data, name="%s-%d.%s" % (base, i, ext)),
                    display_order=i,
                )
        else:
            for i, angle in enumerate(ANGLE_LABELS):
                png = watch_images.render(
                    d["brand"], d["model"], d["ref"], d["material"], d["dial"],
                    i, d["year"])
                ProductImage.objects.create(
                    product=product,
                    original=ContentFile(png, name="%s-%s.png" % (base, angle)),
                    display_order=i,
                )

        # Reviews
        for (rt, rb, score, name) in d.get("reviews", []):
            ProductReview.objects.create(
                product=product, title=rt, body=rb, score=score,
                name=name, email="collector@example.com",
                status=ProductReview.APPROVED)

    def _description(self, d):
        return (
            "A %s %s in %s (ref. %s). %s case at %s, powered by a %s movement "
            "with a %s dial on a %s. Water resistant to %s. Offered in %s "
            "condition (%s), %s. Independently authenticated and delivered fully "
            "insured with signature service."
            % (d["condition"].lower(), title_phrase(d), d["material"].lower(),
               d["ref"], d["material"], d["size"], d["movement"],
               d["dial"].lower(), d["bracelet"].lower(), d["water"],
               d["condition"], d["year"], d["box_papers"])
        )

    def _create_demo_user(self):
        from django.conf import settings
        User = get_user_model()
        email = settings.DEMO_USER_EMAIL
        if not User.objects.filter(email=email).exists():
            # Django's stock User model is username-based; Oscar logs in by
            # email via its EmailBackend, so we mirror the email as username.
            User.objects.create_user(
                username=email, email=email,
                password=settings.DEMO_USER_PASSWORD,
                first_name="Demo", last_name="Collector")

    def _seed_vault(self, num_collectors=40):
        """Dummy market values + vault holdings so the demo shows watches as an
        investment. Real pricing will come from thewatchapi.com later. Seeded
        RNG keeps the demo reproducible."""
        import datetime
        import random
        from decimal import Decimal

        from django.conf import settings

        from apps.vault.models import MarketValue, VaultItem

        random.seed(1234)
        User = get_user_model()
        today = timezone.now().date()

        products = list(Product.objects.all().prefetch_related("stockrecords"))

        def listed(p):
            sr = p.stockrecords.first()
            return Decimal(sr.price) if sr else Decimal("0")

        def round50(value):
            return Decimal(int(round(value / 50)) * 50)

        # 1. Current market value — mostly appreciated vs. the listing price.
        values = {}
        for p in products:
            base = listed(p)
            if base <= 0:
                continue
            factor = Decimal(str(round(random.uniform(0.88, 1.55), 3)))
            value = round50(base * factor)
            values[p.id] = value
            MarketValue.objects.update_or_create(
                product=p, defaults={"value": value, "updated": today})

        # 2. Collector accounts each watching a random subset → social proof.
        collectors = []
        for i in range(num_collectors):
            email = "collector%02d@example.com" % (i + 1)
            user = User.objects.filter(email=email).first()
            if not user:
                user = User.objects.create_user(
                    username=email, email=email, password="!collector-demo",
                    first_name="Collector", last_name="%02d" % (i + 1))
            collectors.append(user)

        weights = [2, 3, 3, 4, 5, 6, 7, 8, 9, 11, 13, 15, 18, 22, 27, 34]
        for p in products:
            target = min(random.choice(weights), len(collectors))
            for u in random.sample(collectors, target):
                VaultItem.objects.get_or_create(
                    user=u, product=p, defaults={"status": VaultItem.WATCHING})

        # 3. The demo user: a few owned (bought below today's value → a gain)
        #    plus a few they're just watching.
        demo = User.objects.filter(email=settings.DEMO_USER_EMAIL).first()
        if demo:
            VaultItem.objects.filter(user=demo).delete()
            pool = [p for p in products if p.id in values]
            random.shuffle(pool)
            for p in pool[:4]:
                purchase = round50(values[p.id] * Decimal(str(round(random.uniform(0.62, 0.9), 3))))
                VaultItem.objects.create(
                    user=demo, product=p, status=VaultItem.OWNED,
                    purchase_price=purchase,
                    purchase_date=today - datetime.timedelta(days=random.randint(120, 900)))
            for p in pool[4:8]:
                VaultItem.objects.create(user=demo, product=p, status=VaultItem.WATCHING)

    def _create_blog_posts(self):
        from apps.blog.models import Post
        today = timezone.now().date()
        for p in BLOG_POSTS:
            post = Post(
                title=p["title"], author=p["author"], excerpt=p["excerpt"],
                body=p["body"], date=today - datetime.timedelta(days=p["days_ago"]),
                published=True)
            png = _blog_banner(p["title"])
            post.image.save("%s.png" % slugify(p["title"]),
                            ContentFile(png), save=False)
            post.save()


def title_phrase(d):
    return "%s %s" % (d["brand"], d["model"])


def _post_count():
    try:
        from apps.blog.models import Post
        return Post.objects.count()
    except Exception:
        return 0


def _blog_banner(title):
    from PIL import Image, ImageDraw
    w, h = 1200, 600
    img = Image.new("RGB", (w, h), (29, 26, 22))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        shade = int(29 + 18 * t)
        draw.line([(0, y), (w, y)], fill=(shade, shade - 3, shade - 7))
    # gold rule
    draw.rectangle([80, h // 2 - 60, 86, h // 2 + 60], fill=(200, 164, 77))
    font = watch_images.serif(46)
    # wrap title
    words = title.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textbbox((0, 0), trial, font=font)[2] > w - 220:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    y = h // 2 - (len(lines) * 56) // 2
    for line in lines:
        draw.text((120, y), line, font=font, fill=(244, 240, 233))
        y += 60
    draw.text((120, h - 90), "THE PIER & PADDOCK JOURNAL",
              font=watch_images.sans(20), fill=(200, 164, 77))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
