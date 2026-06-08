"""Data model for the Crest membership program.

Because checkout is disabled in this demo, a ``DemoPurchase`` log stands in for
real Oscar orders: creating one is what drives lifetime spend, credit accrual
and tier progression. The marquee live-demo action (Operator Console -> Simulate
purchase) creates a ``DemoPurchase`` and recomputes the member's tier on the
spot. See ``services.py`` for the orchestration; the models stay thin.
"""
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from . import tiers

TWOPLACES = Decimal("0.01")


class ProgramConfig(models.Model):
    """Editable program settings — a single row (id=1). Exposes the tunable
    tier thresholds and credit accrual rate so the demo can show the bands are
    not hardcoded. Use ``ProgramConfig.get()`` to fetch/create the singleton."""

    collector_threshold = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("25000.00"),
        help_text="Lifetime spend (USD) that earns the 3rd crest — Collector.",
    )
    curator_threshold = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("75000.00"),
        help_text="Lifetime spend (USD) that earns the 4th crest — Curator.",
    )
    steward_threshold = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("200000.00"),
        help_text="Lifetime spend (USD) that earns the 5th crest — Steward "
                  "(also reachable by invitation).",
    )
    credit_accrual_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal("0.0200"),
        help_text="Retailer's Credit accrued per purchase, as a fraction of "
                  "spend (e.g. 0.02 = 2%). Applies to Collector+ purchases.",
    )

    class Meta:
        verbose_name = "Program configuration"
        verbose_name_plural = "Program configuration"

    def __str__(self):
        return "Crest program configuration"

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Membership(models.Model):
    """One-to-one Crest profile for a user. ``tier`` and ``crest_count`` are
    cached/derived values kept in sync by :meth:`recompute`."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="membership"
    )
    tier = models.CharField(max_length=20, default=tiers.TIER_NAMES[1])
    crest_count = models.PositiveSmallIntegerField(default=0)
    lifetime_spend = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    purchase_count = models.PositiveIntegerField(default=0)
    credit_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    marketing_opt_in = models.BooleanField(default=False)
    invited = models.BooleanField(
        default=False, help_text="Invited to Steward, independent of spend."
    )
    concierge_channel = models.CharField(
        max_length=12, choices=tiers.CONCIERGE_CHOICES, default=tiers.CONCIERGE_NONE
    )
    # Alert preferences (drive the demo's alerts page).
    alerts_email = models.BooleanField(default=True)
    alerts_sms = models.BooleanField(default=False)
    join_date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ["-lifetime_spend"]

    def __str__(self):
        return "%s — %s (%d crests)" % (self.user, self.tier, self.crest_count)

    # -- Derivation -------------------------------------------------------
    def compute_crest_count(self, config=None):
        """Pure function of spend/opt-in/invite — the rule lives only here."""
        config = config or ProgramConfig.get()
        spend = self.lifetime_spend or Decimal(0)
        crest = 0
        if self.marketing_opt_in:
            crest = 1
        if spend > 0 or self.purchase_count >= 1:
            crest = max(crest, 2)
        if spend >= config.collector_threshold:
            crest = max(crest, 3)
        if spend >= config.curator_threshold:
            crest = max(crest, 4)
        if spend >= config.steward_threshold or self.invited:
            crest = 5
        return crest

    def recompute(self, config=None, save=True):
        """Recompute crest_count, tier name and concierge channel from the
        current spend/opt-in/invite state. Call after any change to those."""
        config = config or ProgramConfig.get()
        self.crest_count = self.compute_crest_count(config)
        self.tier = tiers.tier_name(self.crest_count)
        self.concierge_channel = tiers.concierge_for(self.crest_count)
        if save:
            self.save(update_fields=[
                "crest_count", "tier", "concierge_channel",
            ])
        return self.crest_count

    def recalc_credit_balance(self, save=True):
        total = self.user.credit_transactions.aggregate(
            s=models.Sum("amount")
        )["s"] or Decimal(0)
        self.credit_balance = total.quantize(TWOPLACES)
        if save:
            self.save(update_fields=["credit_balance"])
        return self.credit_balance

    # -- Convenience flags used by templates/views ------------------------
    def has_benefit(self, key):
        for b in tiers.BENEFITS:
            if b["key"] == key:
                return self.crest_count >= b["crest"]
        return False

    @property
    def is_by_invitation(self):
        """Steward reached purely by invite rather than spend."""
        if self.crest_count < 5:
            return False
        return self.lifetime_spend < ProgramConfig.get().steward_threshold

    def next_threshold(self, config=None):
        """(label, amount_needed, target_total) toward the next crest, or None
        if at the top tier. Drives the dashboard progress bar."""
        config = config or ProgramConfig.get()
        spend = self.lifetime_spend or Decimal(0)
        ladder = [
            (3, "Collector", config.collector_threshold),
            (4, "Curator", config.curator_threshold),
            (5, "Steward", config.steward_threshold),
        ]
        for crest, label, target in ladder:
            if self.crest_count < crest:
                return {"label": label, "remaining": max(Decimal(0), target - spend),
                        "target": target, "current": spend}
        return None


class DemoPurchase(models.Model):
    """A simulated order. Demo stand-in for real Oscar orders (checkout is
    disabled). Creating one drives spend/credit/tier — orchestrated in
    ``services.record_demo_purchase``."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="demo_purchases"
    )
    product = models.ForeignKey(
        "catalogue.Product", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="demo_purchases",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return "%s — $%s" % (self.user, self.amount)


class CreditTransaction(models.Model):
    """A movement of Retailer's Credit. ``credit_balance`` is the running sum.
    Retailer's Credit is a Pier & Paddock-funded store credit."""

    ACCRUED, REDEEMED, ADJUSTED = "accrued", "redeemed", "adjusted"
    TYPE_CHOICES = (
        (ACCRUED, "Accrued"),
        (REDEEMED, "Redeemed"),
        (ADJUSTED, "Adjusted"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="credit_transactions",
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        help_text="Positive accrues credit; negative redeems/reduces it.",
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=ACCRUED)
    date = models.DateTimeField(default=timezone.now)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return "%s %s $%s" % (self.user, self.type, self.amount)


class GrailEntry(models.Model):
    """A piece a Collector+ member is hunting. Admin flips it to 'matched'."""

    WATCHING, MATCHED = "watching", "matched"
    STATUS_CHOICES = ((WATCHING, "Watching"), (MATCHED, "Matched"))

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="grail_entries"
    )
    brand = models.CharField(max_length=80)
    model = models.CharField(max_length=120)
    reference = models.CharField(max_length=80, blank=True)
    target_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=WATCHING)
    created_date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ["-created_date"]
        verbose_name = "Grail entry"
        verbose_name_plural = "Grail entries"

    def __str__(self):
        return "%s %s (%s)" % (self.brand, self.model, self.get_status_display())


class EarlyAccessListing(models.Model):
    """Flags a product as members-only 'first look' for a minimum crest level
    during a window — it appears in qualifying members' Vaults before the
    public listing goes live."""

    product = models.ForeignKey(
        "catalogue.Product", on_delete=models.CASCADE, related_name="early_access"
    )
    visible_to_min_crest = models.PositiveSmallIntegerField(
        default=4, help_text="Minimum crest count that can see this first (e.g. 4 = Curator)."
    )
    window_start = models.DateTimeField(default=timezone.now)
    window_end = models.DateTimeField()

    class Meta:
        ordering = ["-window_start"]

    def __str__(self):
        return "First-look: %s (crest %d+)" % (self.product, self.visible_to_min_crest)

    @property
    def is_active(self):
        now = timezone.now()
        return self.window_start <= now <= self.window_end


class Invitation(models.Model):
    """An invitation that elevates a member to Steward by invite."""

    email = models.EmailField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="invitations",
    )
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="invitations_issued",
    )
    issued_date = models.DateField(default=timezone.now)
    accepted = models.BooleanField(default=False)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-issued_date"]

    def __str__(self):
        return "Invitation -> %s" % self.email


class MarketReport(models.Model):
    """A quarterly market report artifact. Demo ships a seeded HTML sample."""

    quarter_label = models.CharField(max_length=40)  # e.g. "Q1 2026"
    headline = models.CharField(max_length=200, blank=True)
    content = models.TextField(
        blank=True, help_text="HTML/markdown body (demo). Production may attach a PDF."
    )
    min_crest = models.PositiveSmallIntegerField(
        default=2, help_text="Minimum crest count to read (default 2 = Patron)."
    )
    published = models.DateField(default=timezone.now)

    class Meta:
        ordering = ["-published"]

    def __str__(self):
        return self.quarter_label


class Notification(models.Model):
    """An on-site alert in the member's feed (first-look, grail match, restock).
    Seeded for the demo so the feed looks populated."""

    FIRST_LOOK, GRAIL_MATCH, RESTOCK, PRICE, PROGRAM = (
        "first_look", "grail_match", "restock", "price", "program",
    )
    KIND_CHOICES = (
        (FIRST_LOOK, "First look"),
        (GRAIL_MATCH, "Grail match"),
        (RESTOCK, "Restock"),
        (PRICE, "Price alert"),
        (PROGRAM, "Program"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="loyalty_notifications"
    )
    kind = models.CharField(max_length=12, choices=KIND_CHOICES, default=PROGRAM)
    title = models.CharField(max_length=160)
    body = models.CharField(max_length=400, blank=True)
    url = models.CharField(max_length=300, blank=True)
    created = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return "%s: %s" % (self.user, self.title)
