"""AI-discovery layer for product detail pages.

Generates product-specific FAQs and a schema.org JSON-LD @graph (Product + Offer +
FAQPage + BreadcrumbList + Organization) so PDPs are legible to answer engines and
AI crawlers. Kept in Python so it's testable and the templates stay clean.
"""
from django.conf import settings

CONDITION_SCHEMA = {
    "new": "https://schema.org/NewCondition",
    "unworn": "https://schema.org/NewCondition",
    "pre-owned excellent": "https://schema.org/UsedCondition",
    "pre-owned": "https://schema.org/UsedCondition",
    "used": "https://schema.org/UsedCondition",
}

# (attribute code, human label) surfaced as schema additionalProperty + used in FAQs.
SPEC_FIELDS = [
    ("reference", "Reference"),
    ("case_material", "Case material"),
    ("case_size", "Case size"),
    ("movement", "Movement"),
    ("dial_color", "Dial"),
    ("bracelet", "Bracelet / strap"),
    ("water_resistance", "Water resistance"),
    ("year", "Year"),
    ("box_papers", "Box & papers"),
    ("condition", "Condition"),
]


def _attr(product, code):
    val = getattr(product.attr, code, None)
    return str(val) if val not in (None, "") else ""


def _abs(request, url):
    if not url:
        return ""
    if url.startswith(("http://", "https://")):
        return url
    if request is not None:
        return request.build_absolute_uri(url)
    return settings.LIFESTYLE_BASE_URL.rstrip("/") + url


def _stockrecord(product):
    return product.stockrecords.first()


def _images(request, product, limit=3):
    urls = []
    for pi in product.images.all()[:limit]:
        try:
            urls.append(_abs(request, pi.original.url))
        except Exception:
            continue
    return urls


def product_faqs(product):
    """Product-specific Q&A generated from attributes + house policy. Real, useful
    answers (not boilerplate) so answer engines can extract them."""
    title = product.title
    brand = _attr(product, "brand") or "timepiece"
    model = _attr(product, "model")
    faqs = []

    faqs.append((
        "Is the %s authentic?" % title,
        "Yes. Every %s we offer is independently authenticated by our watch "
        "specialists before it is listed, and delivered with a certificate of "
        "authenticity. Box and papers are verified where present." % brand,
    ))

    cond = _attr(product, "condition")
    year = _attr(product, "year")
    if cond:
        faqs.append((
            "What condition is the %s in?" % title,
            "This %s is graded “%s”%s. Condition is assessed by our "
            "specialists and the listing photos show the actual piece."
            % (title, cond, (", and dates to %s" % year) if year else ""),
        ))

    movement = _attr(product, "movement")
    material = _attr(product, "case_material")
    size = _attr(product, "case_size")
    if movement or material:
        specs = ", ".join(filter(None, [
            ("a %s movement" % movement) if movement else "",
            ("a %s case" % material) if material else "",
            ("measuring %s" % size) if size else "",
        ]))
        faqs.append((
            "What are the key specifications of the %s?" % title,
            "The %s features %s." % (title, specs),
        ))

    water = _attr(product, "water_resistance")
    if water:
        faqs.append((
            "Is the %s water resistant?" % title,
            "The %s is water resistant to %s." % (title, water),
        ))

    bp = _attr(product, "box_papers")
    if bp:
        faqs.append((
            "What is included with the %s?" % title,
            "This %s is offered as “%s.”" % (model or title, bp),
        ))

    faqs.append((
        "How is the %s shipped?" % title,
        "Every order ships fully insured with signature-required overnight "
        "delivery, at no charge. Saturday delivery is available on request.",
    ))

    faqs.append((
        "How do I purchase or reserve the %s?" % title,
        "Add it to your cart to begin, or contact a %s specialist to reserve the "
        "piece or arrange a private viewing." % settings.BRAND_NAME,
    ))

    return [{"q": q, "a": a} for q, a in faqs]


def _org(request):
    from django.templatetags.static import static
    return {
        "@type": "Organization",
        "@id": _abs(request, "/") + "#organization",
        "name": settings.BRAND_NAME,
        "url": _abs(request, "/"),
        "logo": {"@type": "ImageObject", "url": _abs(request, static("img/crest.ico"))},
    }


def _breadcrumbs(request, product):
    items = [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": _abs(request, "/")},
        {"@type": "ListItem", "position": 2, "name": "Shop", "item": _abs(request, "/shop/")},
    ]
    brand = _attr(product, "brand")
    cat = product.categories.first()
    if brand and cat:
        items.append({"@type": "ListItem", "position": 3, "name": brand,
                      "item": _abs(request, "/shop/?brand=%s" % cat.slug)})
    items.append({"@type": "ListItem", "position": len(items) + 1,
                  "name": product.title, "item": _abs(request, product.get_absolute_url())})
    return {"@type": "BreadcrumbList", "itemListElement": items}


def product_jsonld(product, request):
    url = _abs(request, product.get_absolute_url())
    brand = _attr(product, "brand")
    sr = _stockrecord(product)
    cond_url = CONDITION_SCHEMA.get(_attr(product, "condition").lower())

    brand_node = None
    if brand:
        brand_node = {"@type": "Brand", "name": brand}
        from .brand_stories import get_brand_story
        story = get_brand_story(brand)
        if story:
            brand_node["description"] = story["text"]

    node = {
        "@type": "Product",
        "@id": url + "#product",
        "name": product.title,
        "description": (product.description or "").strip(),
        "url": url,
        "brand": brand_node,
        "sku": product.upc or _attr(product, "reference"),
        "mpn": _attr(product, "reference"),
        "category": ", ".join(c.name for c in product.categories.all()) or None,
        "image": _images(request, product) or None,
        "itemCondition": cond_url,
    }
    props = []
    for code, label in SPEC_FIELDS:
        v = _attr(product, code)
        if v:
            props.append({"@type": "PropertyValue", "name": label, "value": v})
    if props:
        node["additionalProperty"] = props

    if sr is not None:
        node["offers"] = {
            "@type": "Offer",
            "url": url,
            "priceCurrency": sr.price_currency,
            "price": str(sr.price),
            "availability": ("https://schema.org/InStock"
                             if (sr.num_in_stock or 0) > 0 else "https://schema.org/OutOfStock"),
            "itemCondition": cond_url,
            "seller": {"@id": _org(request)["@id"]},
        }

    graph = [_org(request), _breadcrumbs(request, product),
             {k: v for k, v in node.items() if v is not None}]

    faqs = product_faqs(product)
    if faqs:
        graph.append({
            "@type": "FAQPage",
            "@id": url + "#faq",
            "mainEntity": [{
                "@type": "Question", "name": f["q"],
                "acceptedAnswer": {"@type": "Answer", "text": f["a"]},
            } for f in faqs],
        })

    return {"@context": "https://schema.org", "@graph": graph}
