"""PDP AI-discovery template tags: product FAQs + JSON-LD + OG image."""
import json

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from ..seo import product_faqs as _product_faqs, product_jsonld

register = template.Library()


@register.simple_tag
def product_faqs(product):
    """List of {q, a} for the visible FAQ section."""
    try:
        return _product_faqs(product)
    except Exception:
        return []


@register.simple_tag(takes_context=True)
def product_jsonld_script(context):
    """schema.org JSON-LD (Product + Offer + FAQPage + BreadcrumbList) for the PDP."""
    product = context.get("product")
    request = context.get("request")
    if product is None:
        return ""
    try:
        data = product_jsonld(product, request)
        payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        return format_html('<script type="application/ld+json">{}</script>', mark_safe(payload))
    except Exception:
        return ""


@register.simple_tag
def brand_story(brand):
    """{'brand', 'text'} for a product's brand, or None."""
    from ..brand_stories import get_brand_story

    return get_brand_story(brand)


@register.simple_tag
def watch_style(product):
    """{'key', 'label', 'snippet'} — the product's house style (from the stored attribute)."""
    from ..watch_styles import product_style

    key, label, snippet = product_style(product)
    return {"key": key, "label": label, "snippet": snippet}


@register.simple_tag
def nav_styles():
    """Ordered [(key, label)] of house styles that have products — for the Shop nav."""
    from ..watch_styles import styles_present

    return styles_present()


@register.simple_tag
def all_watch_styles():
    """[(key, label)] of all twelve styles — for the add-listing dropdown."""
    from ..watch_styles import all_styles

    return all_styles()


@register.simple_tag(takes_context=True)
def product_og_image(context):
    """Absolute URL of the product's primary image for OpenGraph/Twitter."""
    product = context.get("product")
    request = context.get("request")
    if product is None:
        return ""
    try:
        img = product.primary_image()
        original = img.original if hasattr(img, "original") else None
        if not original:
            return ""
        url = original.url
        return request.build_absolute_uri(url) if request is not None else url
    except Exception:
        return ""
