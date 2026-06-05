"""The Vault — lets a collector watch and track the value of watches as an
investment, and (after buying with Pier & Paddock) record what they own.

Market values are dummy data for now; later they'll be sourced from
https://www.thewatchapi.com for real historical pricing.
"""
from decimal import Decimal

from django.conf import settings
from django.db import models


class MarketValue(models.Model):
    """The latest (current) market value for a watch model — dummy for now."""

    product = models.OneToOneField(
        "catalogue.Product", on_delete=models.CASCADE, related_name="market_value"
    )
    value = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=12, default="USD")
    updated = models.DateField()

    def __str__(self):
        return "%s — %s" % (self.product, self.value)


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
