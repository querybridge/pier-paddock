"""Seed the Crest membership demo.

Creates one logged-in-ready member per tier (Member -> Steward) so the presenter
can walk each experience, plus the supporting data every screen needs to look
populated: valuation history for the catalogue (sparklines + premium-to-retail),
a sample quarterly market report, a couple of first-look flags, and seeded
credit / grail / notification records.

Idempotent: re-running resets the five demo members' loyalty state and refreshes
valuations. Existing catalogue/collector accounts are left intact (their
Memberships are ensured + recomputed). Values are deterministic (seeded RNG).

    python manage.py load_loyalty_demo
"""
import datetime
import random
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from oscar.core.loading import get_model

from apps.loyalty import services, tiers
from apps.loyalty.models import (
    CreditTransaction,
    EarlyAccessListing,
    GrailEntry,
    Invitation,
    MarketReport,
    Membership,
    Notification,
    ProgramConfig,
)
from apps.vault.models import MarketValue, VaultItem

Product = get_model("catalogue", "Product")
User = get_user_model()

# Staff "retailer operator" account — for demoing the Operator Console (/console/)
# as the retailer/back-office, separate from the all-powerful superuser admin.
# is_staff (not superuser): exactly what the StaffConsoleMixin gate requires.
RETAILER_EMAIL = "retailer@pierpaddock.demo"
RETAILER_PASSWORD = "Retail1234!"

# Merchant persona for the Merchant Portal (/merchant/) — a generic stand-in for
# the IDC-style dropship supplier (kept invisible in the storefront UI). Staff,
# linked to the catalogue's Oscar Partner, NOT a superuser. Deliberately distinct
# from the loyalty "retailer/operator" account so the two roles don't blur.
MERCHANT_EMAIL = "merchant@meridianwatch.demo"
MERCHANT_PASSWORD = "Merchant1234!"
MERCHANT_NAME = "Meridian Watch Supply"
MERCHANT_SALE_NOTE = "Merchant feed sale (seeded)"

# (login, tier-target spend, purchase_count, first/last name)
PERSONAS = [
    ("member@pierpaddock.demo", Decimal("0"), 0, "Mara", "Ellison"),
    ("patron@pierpaddock.demo", Decimal("9500"), 1, "Paul", "Tran"),
    ("collector@pierpaddock.demo", Decimal("40000"), 3, "Cora", "Bianchi"),
    ("curator@pierpaddock.demo", Decimal("110000"), 7, "Curtis", "Adeyemi"),
    ("steward@pierpaddock.demo", Decimal("260000"), 14, "Stella", "Whitlock"),
]

GRAILS = [
    ("Patek Philippe", "Nautilus 5711/1A", "5711/1A-010", Decimal("135000")),
    ("Audemars Piguet", "Royal Oak Jumbo", "16202ST", Decimal("85000")),
    ("Rolex", "Daytona 'Paul Newman'", "6239", Decimal("210000")),
    ("F.P. Journe", "Chronomètre Bleu", "CB", Decimal("55000")),
]


class Command(BaseCommand):
    help = "Seed the Crest membership demo (per-tier members + supporting data)."

    def handle(self, *args, **options):
        random.seed(4242)
        self.today = timezone.now().date()
        ProgramConfig.get()  # ensure singleton exists

        self._backfill_valuations()
        self._seed_market_report()
        members = self._seed_personas()
        self._seed_first_look(members)
        self._seed_retailer()
        self._seed_merchant_portal()
        self._ensure_all_memberships()

        self.stdout.write(self.style.SUCCESS(
            "Crest demo seeded. Members (password: %s):" % settings.LOYALTY_DEMO_PASSWORD))
        for login, *_ in PERSONAS:
            ms = Membership.objects.get(user__email=login)
            self.stdout.write("  %-28s %s (%d crests)" % (login, ms.tier, ms.crest_count))
        self.stdout.write("  %-28s Operator Console (staff) — password: %s"
                          % (RETAILER_EMAIL, RETAILER_PASSWORD))
        self.stdout.write("  %-28s Merchant Portal (%s, staff) — password: %s"
                          % (MERCHANT_EMAIL, MERCHANT_NAME, MERCHANT_PASSWORD))

    # ------------------------------------------------------------------ #
    def _backfill_valuations(self):
        """Add retail_price + a value history to every catalogued watch so the
        Vault sparkline and premium-to-retail figures render."""
        products = list(Product.objects.all().prefetch_related("stockrecords"))
        n = 0
        for p in products:
            sr = p.stockrecords.first()
            if not sr:
                continue
            retail = Decimal(sr.price)
            mv = getattr(p, "market_value", None)
            current = Decimal(mv.value) if mv else self._round50(retail * Decimal("1.15"))
            history = self._history(retail, current, points=9)
            MarketValue.objects.update_or_create(
                product=p,
                defaults={
                    "value": current,
                    "retail_price": retail,
                    "value_history": history,
                    "updated": self.today,
                },
            )
            n += 1
        self.stdout.write("  valuations backfilled: %d" % n)

    def _history(self, retail, current, points=9):
        """A gently noisy monthly path from ~retail to current value."""
        start = float(retail)
        end = float(current)
        rows = []
        for i in range(points):
            t = i / (points - 1)
            base = start + (end - start) * t
            noise = base * random.uniform(-0.03, 0.03)
            d = self.today - datetime.timedelta(days=30 * (points - 1 - i))
            rows.append({"date": d.isoformat(), "value": int(round((base + noise) / 50) * 50)})
        rows[-1]["value"] = int(current)  # land exactly on current
        return rows

    def _seed_market_report(self):
        MarketReport.objects.update_or_create(
            quarter_label="Q2 2026",
            defaults={
                "headline": "Steel sports models cool as independents climb",
                "min_crest": 2,
                "published": self.today,
                "content": (
                    "<p>The secondary market continued its measured normalisation this "
                    "quarter. Steel sports references from the majors eased a further "
                    "3–6% from their peaks, while independent makers — F.P. Journe, "
                    "H. Moser, Rexhep Rexhepi — extended their run on persistent scarcity.</p>"
                    "<h3>What we're watching</h3>"
                    "<p>Complicated pieces with verified provenance are holding a clear "
                    "premium. Box-and-papers completeness is now worth materially more at "
                    "resale than a year ago.</p>"
                    "<h3>For your Vault</h3>"
                    "<p>If you hold steel sports models, the data suggests patience over "
                    "the next two quarters. Our concierge desk can model specific "
                    "scenarios for your collection on request.</p>"
                ),
            },
        )
        self.stdout.write("  market report seeded")

    # ------------------------------------------------------------------ #
    def _watch_pool(self):
        pool = list(Product.objects.browsable().prefetch_related("stockrecords"))
        random.shuffle(pool)
        return pool

    def _seed_personas(self):
        pool = self._watch_pool()
        members = {}
        cursor = 0

        for login, spend, pcount, first, last in PERSONAS:
            user = User.objects.filter(email=login).first()
            if not user:
                user = User.objects.create_user(
                    username=login, email=login,
                    password=settings.LOYALTY_DEMO_PASSWORD,
                    first_name=first, last_name=last)
            else:
                user.set_password(settings.LOYALTY_DEMO_PASSWORD)
                user.first_name, user.last_name = first, last
                user.save()

            # Reset this member's loyalty + vault state for a clean reseed.
            VaultItem.objects.filter(user=user).delete()
            GrailEntry.objects.filter(user=user).delete()
            CreditTransaction.objects.filter(user=user).delete()
            Notification.objects.filter(user=user).delete()
            user.demo_purchases.all().delete()
            Invitation.objects.filter(user=user).delete()

            ms = services.get_membership(user)
            ms.lifetime_spend = spend
            ms.purchase_count = pcount
            ms.marketing_opt_in = True
            ms.invited = False
            ms.credit_balance = Decimal("0")
            ms.join_date = self.today - datetime.timedelta(days=random.randint(120, 1400))
            ms.save()
            ms.recompute()

            # Give each member some watches: own a few, watch a few.
            mine = pool[cursor:cursor + 7]
            cursor += 7
            owned_n = {0: 0, 1: 1, 2: 3, 3: 4, 4: 5}.get(ms.crest_count, 2)
            for idx, p in enumerate(mine):
                mv = getattr(p, "market_value", None)
                if idx < owned_n and mv:
                    purchase = self._round50(Decimal(mv.value) * Decimal(str(round(random.uniform(0.6, 0.92), 3))))
                    VaultItem.objects.create(
                        user=user, product=p, status=VaultItem.OWNED,
                        purchase_price=purchase,
                        purchase_date=self.today - datetime.timedelta(days=random.randint(90, 1000)))
                else:
                    VaultItem.objects.create(user=user, product=p, status=VaultItem.WATCHING)

            members[login] = ms
            self._persona_extras(login, user, ms)

        return members

    def _persona_extras(self, login, user, ms):
        """Tier-specific colour so each screen demos well."""
        # Collector+: Retailer's Credit balance + grail entries + first-alert.
        if ms.crest_count >= 3:
            services.grant_credit(user, Decimal("1250"), note="Accrued on recent acquisition",
                                  type=CreditTransaction.ACCRUED, _recompute=False)
            ms.recalc_credit_balance()
            for brand, model, ref, target in GRAILS[:2]:
                GrailEntry.objects.create(user=user, brand=brand, model=model,
                                          reference=ref, target_price=target)
            Notification.objects.create(
                user=user, kind=Notification.PRICE,
                title="A piece on your watchlist moved",
                body="One of your watched references is up 4% this month.",
                created=timezone.now() - datetime.timedelta(days=2))

        if login == "patron@pierpaddock.demo":
            services.notify(user, Notification.RESTOCK,
                            title="Back in stock: a piece you viewed",
                            body="An item you looked at is available again.")

        if login == "curator@pierpaddock.demo":
            # A grail + a first-look notification (the listing itself is seeded later).
            b = GRAILS[2]
            GrailEntry.objects.create(user=user, brand=b[0], model=b[1], reference=b[2], target_price=b[3])
            services.notify(user, Notification.FIRST_LOOK,
                            title="A members-only first look is in your Vault",
                            body="A new arrival is visible to you before it lists publicly.")

        if login == "steward@pierpaddock.demo":
            # By-invitation example + a matched grail.
            Invitation.objects.create(email=user.email, user=user, accepted=True,
                                      note="Marquee invitation (demo)")
            ms.invited = True
            ms.save(update_fields=["invited"])
            ms.recompute()
            g = GrailEntry.objects.create(user=user, brand=GRAILS[3][0], model=GRAILS[3][1],
                                          reference=GRAILS[3][2], target_price=GRAILS[3][3])
            services.mark_grail_matched(g)

    def _seed_first_look(self, members):
        """Flag two pieces as first-look for Curator+ so they show in those
        members' Vaults before public listing."""
        EarlyAccessListing.objects.all().delete()
        pool = list(Product.objects.browsable())
        random.shuffle(pool)
        now = timezone.now()
        for p in pool[:2]:
            EarlyAccessListing.objects.create(
                product=p, visible_to_min_crest=4,
                window_start=now - datetime.timedelta(days=1),
                window_end=now + datetime.timedelta(days=5))
        self.stdout.write("  first-look flags seeded: 2 (Curator+)")

    def _seed_retailer(self):
        """Create/refresh the retailer-operator staff account used to demo the
        Operator Console. Staff but NOT superuser, so it shows exactly the
        back-office a retailer would use — no Django superuser powers."""
        user = User.objects.filter(email=RETAILER_EMAIL).first()
        if not user:
            user = User.objects.create_user(
                username=RETAILER_EMAIL, email=RETAILER_EMAIL,
                password=RETAILER_PASSWORD,
                first_name="Demo", last_name="Operator")
        else:
            user.set_password(RETAILER_PASSWORD)
            user.first_name, user.last_name = "Demo", "Operator"
        user.is_staff = True
        user.is_superuser = False
        user.is_active = True
        user.save()
        self.stdout.write("  retailer operator seeded: %s (staff)" % RETAILER_EMAIL)

    def _seed_merchant_portal(self):
        """Set up the Merchant Portal demo: a merchant profile on the catalogue's
        Partner, a staff supplier account linked to it, and a seeded sales
        history (DemoPurchase rows scoped to that partner's products) so the
        sales monitor looks alive. Sales history is attributed to background
        collector buyers and does NOT touch the tier personas' spend."""
        import datetime

        from oscar.core.loading import get_model
        from apps.loyalty.models import DemoPurchase
        from apps.merchant.models import MerchantProfile

        Partner = get_model("partner", "Partner")
        Product = get_model("catalogue", "Product")

        partner = Partner.objects.first()
        if partner is None:
            self.stdout.write("  merchant portal skipped (no Partner found)")
            return

        profile, _ = MerchantProfile.objects.get_or_create(partner=partner)
        profile.display_name = MERCHANT_NAME
        profile.contact_email = "ops@meridianwatch.demo"
        profile.feed_url = "https://feeds.meridianwatch.demo/pierpaddock.xml"
        profile.feed_enabled = True
        profile.last_synced = timezone.now() - datetime.timedelta(hours=6)
        profile.last_sync_result = "Synced — %d listings reconciled." % (
            partner.stockrecords.values("product").distinct().count())
        profile.save()

        # Supplier staff account, linked to the partner.
        user = User.objects.filter(email=MERCHANT_EMAIL).first()
        if not user:
            user = User.objects.create_user(
                username=MERCHANT_EMAIL, email=MERCHANT_EMAIL,
                password=MERCHANT_PASSWORD, first_name="Meridian", last_name="Supply")
        else:
            user.set_password(MERCHANT_PASSWORD)
        user.is_staff = True
        user.is_superuser = False
        user.is_active = True
        user.save()
        partner.users.add(user)
        # Merchants are not members — drop any membership the signal auto-created.
        Membership.objects.filter(user=user).delete()

        # Seeded sales history (idempotent: drop prior seeded rows first).
        DemoPurchase.objects.filter(note=MERCHANT_SALE_NOTE).delete()
        products = list(
            Product.objects.filter(stockrecords__partner=partner)
            .distinct().prefetch_related("stockrecords")
        )
        buyers = list(User.objects.filter(email__startswith="collector").order_by("email"))
        if not buyers:
            buyers = list(User.objects.filter(email=settings.DEMO_USER_EMAIL))
        now = timezone.now()
        made = 0
        if products and buyers:
            # ~65 sales spread over the last ~6 months, a handful this month.
            for i in range(65):
                p = random.choice(products)
                sr = p.stockrecords.filter(partner=partner).first()
                if not sr:
                    continue
                amount = self._round50(Decimal(sr.price) * Decimal(str(round(random.uniform(0.94, 1.06), 3))))
                days_ago = random.randint(0, 185)
                DemoPurchase.objects.create(
                    user=random.choice(buyers), product=p, amount=amount,
                    date=now - datetime.timedelta(days=days_ago, hours=random.randint(0, 23)),
                    note=MERCHANT_SALE_NOTE)
                made += 1
        self.stdout.write("  merchant portal seeded: %s (%s), %d sales"
                          % (MERCHANT_EMAIL, MERCHANT_NAME, made))

    def _ensure_all_memberships(self):
        """Every customer (incl. pre-existing demo/collector/admin accounts
        created before the membership signal) gets a Membership, recomputed.
        Merchants are excluded — they're suppliers, not members."""
        from apps.merchant.models import is_merchant

        created = 0
        for u in User.objects.all():
            if u.is_staff and is_merchant(u):
                Membership.objects.filter(user=u).delete()
                continue
            ms, was_created = Membership.objects.get_or_create(user=u)
            if was_created:
                # Pre-existing collectors: opt them in so the tier counts look alive.
                ms.marketing_opt_in = True
                ms.save(update_fields=["marketing_opt_in"])
                created += 1
            ms.recompute()
        self.stdout.write("  memberships ensured (%d new)" % created)

    # ------------------------------------------------------------------ #
    @staticmethod
    def _round50(value):
        return Decimal(int(round(value / 50)) * 50)
