from decimal import Decimal

from django import template

register = template.Library()

# Order in which watch specs appear on the product detail page.
SPEC_ORDER = [
    "brand", "model", "reference", "case_material", "case_size",
    "movement", "dial_color", "bracelet", "water_resistance",
    "condition", "year", "box_papers",
]


@register.filter
def product_specs(product):
    """Return product attribute values as an ordered list of (label, value)."""
    by_code = {}
    for av in product.attribute_values.select_related("attribute").all():
        by_code[av.attribute.code] = (av.attribute.name, av.value_as_text)
    rows = []
    for code in SPEC_ORDER:
        if code in by_code:
            rows.append(by_code.pop(code))
    # Any extra attributes not in the explicit order.
    rows.extend(by_code.values())
    return rows


@register.filter
def attr(product, code):
    """Fetch a single attribute value by code, or '' if absent."""
    try:
        return getattr(product.attr, code)
    except Exception:
        return ""


@register.filter
def related_products(product, limit=4):
    """Other browsable watches sharing a category (brand/collection), minus self."""
    from oscar.core.loading import get_model

    Product = get_model("catalogue", "Product")
    cat_ids = list(product.categories.values_list("id", flat=True))
    if not cat_ids:
        return []
    qs = (
        Product.objects.browsable()
        .filter(categories__in=cat_ids)
        .exclude(id=product.id)
        .distinct()
    )
    return list(qs[:limit])


@register.filter
def vault_count(product):
    """How many times this product has been saved to a vault (wishlist),
    counted across all collectors."""
    from oscar.core.loading import get_model

    Line = get_model("wishlists", "Line")
    try:
        return Line.objects.filter(product=product).count()
    except Exception:
        return 0


@register.filter
def money(value):
    """Format a price in USD with two decimals, e.g. $13,500.00."""
    if value is None or value == "":
        return ""
    try:
        d = Decimal(value)
    except Exception:
        return value
    return "${:,.2f}".format(d)
