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
