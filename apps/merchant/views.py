"""Merchant Portal views — a branded, supplier-scoped back office at /merchant/.

Gated to a staff user linked to a merchant Partner (or a superuser). Each
merchant sees ONLY their own listings and sales. Demo controls (add a listing,
configure/sync the XML feed) are clearly the supplier's own tools.
"""
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.text import slugify
from django.views.generic import TemplateView
from oscar.core.loading import get_model

from .models import MerchantProfile

Product = get_model("catalogue", "Product")
ProductClass = get_model("catalogue", "ProductClass")
ProductImage = get_model("catalogue", "ProductImage")
StockRecord = get_model("partner", "StockRecord")
Category = get_model("catalogue", "Category")


def _decimal(raw, default=None):
    if raw in (None, ""):
        return default
    try:
        return Decimal(str(raw).replace(",", "").replace("$", "").strip())
    except (InvalidOperation, AttributeError):
        return default


class MerchantPortalMixin(UserPassesTestMixin):
    """Access for staff linked to a merchant Partner (superusers see the first
    merchant, for convenience). Resolves ``self.profile``."""
    raise_exception = False

    def _resolve_profile(self):
        user = self.request.user
        if not user.is_authenticated:
            return None
        qs = MerchantProfile.objects.select_related("partner")
        if user.is_superuser:
            return qs.first()
        if user.is_staff:
            return qs.filter(partner__users=user).first()
        return None

    def test_func(self):
        self.profile = self._resolve_profile()
        return self.profile is not None

    def handle_no_permission(self):
        # Anonymous -> Operations sign-in (with ?next); a signed-in operator who
        # landed here -> the Operator Console.
        from apps.core.operations import route_to_operations
        return route_to_operations(self.request, self.request.path)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["profile"] = self.profile
        ctx["merchant"] = self.profile.name
        ctx["portal_section"] = getattr(self, "portal_section", "")
        return ctx


class DashboardView(MerchantPortalMixin, TemplateView):
    template_name = "merchant/dashboard.html"
    portal_section = "dashboard"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["summary"] = self.profile.sales_summary()
        ctx["top"] = self.profile.sales_by_product()[:5]
        ctx["listing_count"] = self.profile.listing_count()
        ctx["feed_connected"] = bool(self.profile.feed_url and self.profile.feed_enabled)
        return ctx


class ListingsView(MerchantPortalMixin, TemplateView):
    template_name = "merchant/listings.html"
    portal_section = "listings"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Per-product units sold, for the listings table.
        sold = {r["product_id"]: r["units"] for r in self.profile.sales_by_product()}
        rows = []
        for p in self.profile.products().prefetch_related("stockrecords"):
            sr = p.stockrecords.filter(partner=self.profile.partner).first()
            rows.append({
                "product": p,
                "sku": sr.partner_sku if sr else "",
                "price": sr.price if sr else None,
                "stock": sr.num_in_stock if sr else 0,
                "units_sold": sold.get(p.id, 0),
            })
        ctx["rows"] = rows
        return ctx

    def post(self, request, *args, **kwargs):
        """Manually add a listing — creates a Watch product + stockrecord under
        this merchant's partner, with a generated placeholder image so it shows
        in the storefront immediately."""
        brand = (request.POST.get("brand") or "").strip()
        model = (request.POST.get("model") or "").strip()
        ref = (request.POST.get("reference") or "").strip()
        price = _decimal(request.POST.get("price"))
        stock = request.POST.get("stock") or "1"
        if not brand or not model or price is None:
            messages.error(request, "Brand, model and price are required.")
            return redirect("merchant:listings")
        try:
            self._create_listing(brand, model, ref, price, int(stock),
                                  condition=(request.POST.get("condition") or "Pre-Owned"),
                                  material=(request.POST.get("material") or "Stainless Steel"),
                                  style=(request.POST.get("style") or ""))
        except Exception as e:  # keep the demo resilient
            messages.error(request, "Could not create listing: %s" % e)
            return redirect("merchant:listings")
        messages.success(request, "Listing added — %s %s is now live on the storefront." % (brand, model))
        return redirect("merchant:listings")

    def _create_listing(self, brand, model, ref, price, stock, condition, material, style=""):
        from django.core.files.base import ContentFile
        from apps.core import watch_images

        pc = ProductClass.objects.get(name="Watch")
        title = "%s %s" % (brand, model)
        product = Product.objects.create(
            product_class=pc, structure=Product.STANDALONE, title=title,
            upc=slugify("%s-%s-%s" % (brand, ref or model, timezone.now().timestamp()))[:64],
            is_discountable=False,
        )
        # Minimal attribute set (the spec table tolerates blanks).
        product.attr.brand = brand
        product.attr.model = model
        if ref:
            product.attr.reference = ref
        product.attr.case_material = material
        product.attr.condition = condition
        product.attr.save()

        # House style — the merchant's selection, or auto-classified from the title.
        from apps.shop.watch_styles import STYLE_LABEL, classify, set_product_style
        set_product_style(product, style if style in STYLE_LABEL else classify(title))

        # File it under the matching brand category if one exists.
        cat = Category.objects.filter(name__iexact=brand).first()
        if cat:
            product.categories.add(cat)

        StockRecord.objects.create(
            product=product, partner=self.profile.partner,
            partner_sku=ref or slugify(title)[:32],
            price_currency="USD", price=price, num_in_stock=stock,
        )

        # Generated placeholder imagery (primary + a rollover secondary).
        base = slugify(title)
        for i in range(2):
            png = watch_images.render(brand, model, ref, material, "Black", i, timezone.now().year)
            ProductImage.objects.create(
                product=product,
                original=ContentFile(png, name="%s-%d.png" % (base, i)),
                display_order=i,
            )


class FeedView(MerchantPortalMixin, TemplateView):
    template_name = "merchant/feed.html"
    portal_section = "feed"

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        p = self.profile
        if action == "sync":
            # Simulated sync — no real fetch in the demo (see model docstring).
            if not p.feed_url:
                messages.error(request, "Set a feed URL before syncing.")
                return redirect("merchant:feed")
            p.last_synced = timezone.now()
            p.last_sync_result = "Simulated sync — %d listings reconciled (demo)." % p.listing_count()
            p.save(update_fields=["last_synced", "last_sync_result"])
            messages.success(request, "Feed synced (demo) — no external fetch was made.")
        else:
            p.feed_url = (request.POST.get("feed_url") or "").strip()
            p.feed_enabled = bool(request.POST.get("feed_enabled"))
            p.auto_sync = bool(request.POST.get("auto_sync"))
            p.contact_email = (request.POST.get("contact_email") or "").strip()
            p.save(update_fields=["feed_url", "feed_enabled", "auto_sync", "contact_email"])
            messages.success(request, "Feed settings saved.")
        return redirect("merchant:feed")


class SalesView(MerchantPortalMixin, TemplateView):
    template_name = "merchant/sales.html"
    portal_section = "sales"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["summary"] = self.profile.sales_summary()
        ctx["rows"] = self.profile.sales_by_product()
        ctx["recent"] = self.profile.sales_qs().select_related("product")[:15]
        return ctx
