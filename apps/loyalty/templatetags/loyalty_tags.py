"""Template helpers for the Crest program — chiefly the reusable crest mark."""
from django import template

from .. import tiers as tier_defs

register = template.Library()

# Pixel size per named size token, applied to each shield in the row.
CREST_SIZES = {"sm": 16, "md": 26, "lg": 64}


@register.inclusion_tag("loyalty/partials/_crest_row.html")
def crest_row(crest_count, size="md", label=False, max_crests=tier_defs.MAX_CRESTS):
    """Render 1..max_crests shield marks; the first ``crest_count`` are filled
    (earned), the rest are outline (locked). ``size`` is sm|md|lg.

        {% crest_row membership.crest_count size="lg" label=True %}
    """
    try:
        crest_count = int(crest_count or 0)
    except (TypeError, ValueError):
        crest_count = 0
    px = CREST_SIZES.get(size, CREST_SIZES["md"])
    shields = [
        {"index": i, "filled": i <= crest_count}
        for i in range(1, int(max_crests) + 1)
    ]
    return {
        "shields": shields,
        "px": px,
        "size": size,
        "crest_count": crest_count,
        "tier_name": tier_defs.tier_name(crest_count),
        "show_label": label,
    }


@register.simple_tag
def benefits_with_state(crest_count):
    return tier_defs.benefits_with_state(crest_count)


@register.simple_tag
def tier_name(crest_count):
    return tier_defs.tier_name(crest_count)
