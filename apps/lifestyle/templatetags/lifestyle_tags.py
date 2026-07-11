"""Template tags for the Lifestyle magazine: ad zones + data-driven nav."""
from django import template
from django.utils.safestring import mark_safe

from ..models import AdZone

register = template.Library()

# The magazine's fixed primary categories (spec Phase 1). Until the Wagtail
# CategoryPages exist (Phase 2), the nav falls back to these names/slugs.
FIXED_CATEGORIES = [
    ("Fashion", "fashion"),
    ("Motorsports", "motorsports"),
    ("Watersports", "watersports"),
    ("Business", "business"),
    ("Entertainment", "entertainment"),
    ("Health", "health"),
]


@register.simple_tag
def ad_zone(slug):
    """Render an ad slot by slug (Revive tag or local placeholder). Silent if the
    zone doesn't exist so a missing zone never breaks a page."""
    try:
        zone = AdZone.objects.get(slug=slug)
    except AdZone.DoesNotExist:
        return ""
    return zone.render()


@register.simple_tag
def lifestyle_nav():
    """Primary nav items: the six categories (live CategoryPages if present, else
    the fixed fallback) plus Shop → storefront root. Data-driven per spec."""
    items = []
    try:
        from ..models import CategoryPage  # defined in Phase 2

        pages = list(CategoryPage.objects.live().order_by("path"))
    except Exception:
        pages = []

    if pages:
        for p in pages:
            items.append({"title": p.title, "url": p.url})
    else:
        for title, slug in FIXED_CATEGORIES:
            items.append({"title": title, "url": "/lifestyle/%s/" % slug})

    items.append({"title": "Shop", "url": "/"})
    return items


@register.simple_tag
def lifestyle_latest(limit=5, exclude_id=None):
    """Most recent published articles (used by footer/sidebar). Empty until
    ArticlePage exists (Phase 2)."""
    try:
        from ..models import ArticlePage

        qs = ArticlePage.objects.live().public().order_by("-first_published_at")
        if exclude_id:
            qs = qs.exclude(id=exclude_id)
        return list(qs[:limit])
    except Exception:
        return []


@register.inclusion_tag("lifestyle/includes/_latest_news.html", takes_context=True)
def latest_news(context, limit=5):
    """The article rail's 'Latest News' — most recent articles, current excluded."""
    page = context.get("page")
    exclude = getattr(page, "id", None)
    return {"articles": lifestyle_latest(limit, exclude)}


@register.inclusion_tag("lifestyle/includes/_sponsored_products.html", takes_context=True)
def sponsored_products(context, limit=4):
    """Sponsored product units for the article rail.

    Resolution order: curated ``SponsoredProductSlot``s → the article's
    ``related_products`` → same-category / recent products. Each link carries
    ``rel="sponsored"`` and click-through tracking params.

    REVIVE CONTRACT (future): this tag is the seam for a customised Revive
    product-listing zone. When Revive lands, replace the resolution below with a
    call keyed by a zone ID that returns JSON ``[{image, title, url, advertiser}]``;
    the output markup stays identical.
    """
    from ..models import SponsoredProductSlot

    page = context.get("page")
    units = []

    slots = list(SponsoredProductSlot.objects.filter(active=True).select_related("product")[:limit])
    if slots:
        units = [{"product": s.product, "hook": s.hook, "advertiser": s.advertiser} for s in slots]
    elif page is not None and hasattr(page, "related_products"):
        units = [{"product": rp.product, "hook": "", "advertiser": ""}
                 for rp in page.related_products.all()[:limit]]

    if not units and page is not None:
        try:
            from oscar.core.loading import get_model
            Product = get_model("catalogue", "Product")
            units = [{"product": p, "hook": "", "advertiser": ""}
                     for p in Product.objects.browsable()[:limit]]
        except Exception:
            units = []

    slug = getattr(page, "slug", "") or ""
    for u in units:
        try:
            u["url"] = "%s?ppl_src=sponsored&ppl_article=%s" % (u["product"].get_absolute_url(), slug)
        except Exception:
            u["url"] = "#"
    return {"units": units}
