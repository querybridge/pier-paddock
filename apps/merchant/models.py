"""Merchant Portal — the supplier/merchant side of the demo.

A merchant (a stand-in for the IDC-style dropship supplier) lists watches on
Pier & Paddock, keeps their inventory in sync via an XML product feed, and
monitors their sales. Inventory is modelled with Oscar's existing
``partner.Partner`` (every StockRecord already belongs to a Partner), so a
``MerchantProfile`` just decorates a Partner with feed config + a display name.

NB: "merchant" here is the supplier, deliberately distinct from the loyalty
"retailer/operator" (who runs the Operator Console) so the two roles don't blur.

Sales are derived from the loyalty ``DemoPurchase`` log scoped to this partner's
products (checkout is disabled, so DemoPurchase is the stand-in for orders) —
which means the Operator Console's "Simulate purchase" also moves a merchant's
numbers live.
"""
from django.conf import settings
from django.db import models
from django.utils import timezone


class MerchantProfile(models.Model):
    """Decorates an Oscar Partner with a portal display name + XML feed config.

    The XML feed is a configurable but INACTIVE integration in the demo (mirrors
    the SendGrid/Mailchimp pattern): you can set the URL, toggle it, and run a
    simulated "Sync now" that timestamps ``last_synced`` — but nothing is
    actually fetched. Production would parse the feed and upsert StockRecords.
    """

    partner = models.OneToOneField(
        "partner.Partner", on_delete=models.CASCADE, related_name="merchant_profile"
    )
    # Shown in the portal UI instead of the (possibly internal) Partner.name.
    display_name = models.CharField(max_length=120, blank=True)
    contact_email = models.EmailField(blank=True)

    # XML product feed (inactive in the demo).
    feed_url = models.URLField(blank=True)
    feed_format = models.CharField(max_length=12, default="xml")
    feed_enabled = models.BooleanField(default=False)
    auto_sync = models.BooleanField(default=False)
    last_synced = models.DateTimeField(null=True, blank=True)
    last_sync_result = models.CharField(max_length=200, blank=True)

    created = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Merchant profile"

    def __str__(self):
        return self.name

    @property
    def name(self):
        return self.display_name or self.partner.name

    # -- Inventory --------------------------------------------------------
    def products(self):
        """Browsable products this merchant supplies (via their StockRecords)."""
        from oscar.core.loading import get_model

        Product = get_model("catalogue", "Product")
        return (
            Product.objects.filter(stockrecords__partner=self.partner)
            .distinct()
            .order_by("title")
        )

    def listing_count(self):
        return self.partner.stockrecords.values("product").distinct().count()

    # -- Sales (from DemoPurchase scoped to this partner's products) ------
    def sales_qs(self):
        from apps.loyalty.models import DemoPurchase

        return DemoPurchase.objects.filter(
            product__stockrecords__partner=self.partner
        ).distinct()

    def sales_summary(self):
        """Headline numbers for the dashboard."""
        from decimal import Decimal

        from django.db.models import Count, Sum

        qs = self.sales_qs()
        month_start = timezone.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        month = qs.filter(date__gte=month_start).aggregate(
            n=Count("id"), gross=Sum("amount")
        )
        life = qs.aggregate(n=Count("id"), gross=Sum("amount"))
        return {
            "month_units": month["n"] or 0,
            "month_gross": month["gross"] or Decimal(0),
            "life_units": life["n"] or 0,
            "life_gross": life["gross"] or Decimal(0),
        }

    def sales_by_product(self):
        """Per-piece sales monitor rows, best-sellers first."""
        from django.db.models import Count, Sum

        rows = (
            self.sales_qs()
            .values("product_id", "product__title")
            .annotate(units=Count("id"), gross=Sum("amount"))
            .order_by("-units", "-gross")
        )
        return list(rows)
