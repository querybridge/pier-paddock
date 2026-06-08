"""The Vault — lets a collector watch and track the value of watches as an
investment, and (after buying with Pier & Paddock) record what they own.

Market values are dummy data for now; later they'll be sourced from
https://www.thewatchapi.com for real historical pricing.
"""
from decimal import Decimal

from django.conf import settings
from django.db import models


class MarketValue(models.Model):
    """Valuation for a watch model — its current secondary value, the original
    retail price, and a short value history that powers the Vault sparkline.

    This is the spec's ``Valuation`` record. Values are seeded dummy data for
    the demo; in production they'd be sourced from the WatchCharts API
    (historical/secondary pricing).
    """

    product = models.OneToOneField(
        "catalogue.Product", on_delete=models.CASCADE, related_name="market_value"
    )
    value = models.DecimalField(max_digits=12, decimal_places=2)  # current secondary value
    retail_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text="Original retail / list price, for the premium-to-retail figure.",
    )
    currency = models.CharField(max_length=12, default="USD")
    # List of {"date": "YYYY-MM-DD", "value": <number>}, oldest first.
    value_history = models.JSONField(default=list, blank=True)
    updated = models.DateField()

    def __str__(self):
        return "%s — %s" % (self.product, self.value)

    @property
    def premium_to_retail(self):
        """Current value minus retail (positive = trading above retail)."""
        if self.retail_price:
            return self.value - self.retail_price
        return None

    @property
    def premium_pct(self):
        if self.retail_price:
            return (self.value - self.retail_price) / self.retail_price * Decimal(100)
        return None

    def sparkline_points(self, width=120, height=32, pad=2):
        """Return an SVG polyline 'points' string for the value history."""
        pts = [p for p in (self.value_history or []) if p.get("value") is not None]
        if len(pts) < 2:
            return ""
        values = [float(p["value"]) for p in pts]
        lo, hi = min(values), max(values)
        span = (hi - lo) or 1.0
        n = len(values)
        coords = []
        for i, v in enumerate(values):
            x = pad + (width - 2 * pad) * (i / (n - 1))
            y = pad + (height - 2 * pad) * (1 - (v - lo) / span)
            coords.append("%.1f,%.1f" % (x, y))
        return " ".join(coords)


class VaultItem(models.Model):
    """A watch a collector is watching, or owns (bought through Pier & Paddock)."""

    WATCHING, OWNED = "watching", "owned"
    STATUS_CHOICES = ((WATCHING, "Watching"), (OWNED, "Owned"))

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vault_items"
    )
    product = models.ForeignKey(
        "catalogue.Product", on_delete=models.CASCADE, related_name="vault_items"
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=WATCHING)
    purchase_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    purchase_date = models.DateField(null=True, blank=True)
    added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")
        ordering = ["-added"]

    def __str__(self):
        return "%s · %s (%s)" % (self.user, self.product, self.status)

    @property
    def owned(self):
        return self.status == self.OWNED

    @property
    def latest_value(self):
        mv = getattr(self.product, "market_value", None)
        return mv.value if mv else None

    @property
    def gain(self):
        """Change in value vs. what was paid (owned items only)."""
        if self.owned and self.purchase_price is not None and self.latest_value is not None:
            return self.latest_value - self.purchase_price
        return None

    @property
    def gain_pct(self):
        g = self.gain
        if g is not None and self.purchase_price:
            return (g / self.purchase_price) * Decimal(100)
        return None
