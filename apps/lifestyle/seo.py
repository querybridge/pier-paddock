"""Phase 6 — structured data (schema.org JSON-LD) for the Lifestyle magazine.

Built in Python (not templates) so the graph is testable and the markup stays
clean. ``page_jsonld(page, request)`` returns a ``{"@context", "@graph": [...]}``
dict; the ``lifestyle_jsonld`` template tag serialises it into a
``<script type="application/ld+json">`` block.

The primary node's ``@type`` is chosen by ``post_type`` per LIFESTYLE_MAGAZINE.md.
"""
from django.conf import settings
from django.templatetags.static import static

# post_type → primary schema.org @type for the article node.
POST_TYPE_SCHEMA = {
    "standard": "NewsArticle",
    "feature": "NewsArticle",
    "interview": "NewsArticle",
    "event": "NewsArticle",
    "guide": "Article",
    "list": "Article",
    "gallery": "Article",
    "quote": "Article",
    "audio": "Article",
    "video": "Article",
    "review": "Review",
}


def _abs(request, url):
    if not url:
        return ""
    if url.startswith(("http://", "https://")):
        return url
    if request is not None:
        return request.build_absolute_uri(url)
    return settings.LIFESTYLE_BASE_URL.rstrip("/") + url


def _iso(dt):
    return dt.isoformat() if dt else None


def _rendition_url(request, image, spec="width-1200"):
    if not image:
        return None
    try:
        return _abs(request, image.get_rendition(spec).url)
    except Exception:
        return None


def _org_id(request):
    return _abs(request, "/") + "#organization"


def organization(request):
    logo = _abs(request, static("lifestyle/img/pp-lifestyle-logo.svg"))
    return {
        "@type": "Organization",
        "@id": _org_id(request),
        "name": settings.BRAND_NAME,
        "url": _abs(request, "/"),
        "logo": {"@type": "ImageObject", "url": logo},
    }


def website(request):
    return {
        "@type": "WebSite",
        "@id": _abs(request, "/") + "#website",
        "url": _abs(request, "/"),
        "name": settings.WAGTAIL_SITE_NAME,
        "publisher": {"@id": _org_id(request)},
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": _abs(request, "/lifestyle/search/?q={search_term_string}"),
            },
            "query-input": "required name=search_term_string",
        },
    }


def breadcrumbs(request, page):
    items, pos = [], 1
    for anc in page.get_ancestors(inclusive=True):
        url = anc.get_url(request)
        if not url:  # the hidden Wagtail root has no routable URL
            continue
        items.append({
            "@type": "ListItem", "position": pos,
            "name": anc.title, "item": _abs(request, url),
        })
        pos += 1
    return {"@type": "BreadcrumbList", "itemListElement": items}


def _person(request, author):
    same = [u for u in (author.twitter, author.instagram, author.linkedin, author.website) if u]
    node = {"@type": "Person", "name": author.title, "url": author.get_full_url(request)}
    if author.role:
        node["jobTitle"] = author.role
    if same:
        node["sameAs"] = same
    return node


def _faq_node(page):
    """FAQPage from any `faq` StreamField blocks, for answer-engine extraction."""
    import re
    qa = []
    for block in page.body:
        if block.block_type != "faq":
            continue
        for item in block.value.get("items", []):
            answer = re.sub(r"<[^>]+>", " ", str(item.get("answer", ""))).strip()
            question = str(item.get("question", "")).strip()
            if question and answer:
                qa.append({
                    "@type": "Question", "name": question,
                    "acceptedAnswer": {"@type": "Answer", "text": answer},
                })
    if not qa:
        return None
    return {"@type": "FAQPage", "mainEntity": qa}


def _video_node(request, page):
    thumb = _rendition_url(request, page.hero_image or page.og_image)
    node = {
        "@type": "VideoObject",
        "name": page.title,
        "description": page.search_description or page.subtitle or page.title,
        "uploadDate": _iso(page.first_published_at),
        "embedUrl": page.lead_video_url,
    }
    if thumb:
        node["thumbnailUrl"] = [thumb]
    return node


def _product_nodes(request, page):
    """Product schema for the article's shoppable products (no price, per brand rules)."""
    nodes = []
    for rp in page.related_products.all():
        p = rp.product
        try:
            url = _abs(request, p.get_absolute_url())
        except Exception:
            url = None
        node = {"@type": "Product", "name": str(p.title), "url": url}
        brand = getattr(getattr(p, "brand", None), "name", None) or _product_brand(p)
        if brand:
            node["brand"] = {"@type": "Brand", "name": brand}
        img = _product_image(request, p)
        if img:
            node["image"] = img
        nodes.append(node)
    return nodes


def _product_brand(product):
    try:
        attr = product.attribute_values.filter(attribute__code="brand").first()
        return attr.value_as_text if attr else None
    except Exception:
        return None


def _product_image(request, product):
    try:
        img = product.primary_image()
        original = img.original if hasattr(img, "original") else None
        return _abs(request, original.url) if original else None
    except Exception:
        return None


def article_node(request, page):
    url = page.get_full_url(request)
    schema_type = POST_TYPE_SCHEMA.get(page.post_type, "Article")
    image = _rendition_url(request, page.og_image or page.hero_image)
    authors = [_person(request, a) for a in page.authors.all()]
    try:
        word_count = len(page._plain_body().split())
    except Exception:
        word_count = None

    node = {
        "@type": schema_type,
        "@id": url + "#article",
        "url": url,
        "headline": (page.seo_title or page.title)[:110],
        "description": page.search_description or page.subtitle or "",
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "datePublished": _iso(page.first_published_at or page.latest_revision_created_at),
        "dateModified": _iso(page.last_published_at or page.first_published_at),
        "author": authors or [{"@id": _org_id(request)}],
        "publisher": {"@id": _org_id(request)},
        "isAccessibleForFree": True,
    }
    if image:
        node["image"] = [image]
    if word_count:
        node["wordCount"] = word_count
    if page.category:
        node["articleSection"] = page.category.title
    keywords = [t.name for t in page.tags.all()]
    if keywords:
        node["keywords"] = keywords
    if schema_type == "Review":
        node["itemReviewed"] = {"@type": "Thing", "name": page.title}
    return node


def page_jsonld(page, request):
    """Return the schema.org @graph for `page` (an already-specific Wagtail page)."""
    graph = [organization(request), website(request), breadcrumbs(request, page)]

    model = type(page).__name__
    if model == "ArticlePage":
        graph.append(article_node(request, page))
        if page.post_type == "video" and page.lead_video_url:
            graph.append(_video_node(request, page))
        faq = _faq_node(page)
        if faq:
            graph.append(faq)
        graph.extend(_product_nodes(request, page))
    elif model in ("CategoryPage", "LifestyleIndexPage", "AuthorIndexPage", "AuthorPage"):
        graph.append({
            "@type": "CollectionPage",
            "@id": page.get_full_url(request) + "#collection",
            "url": page.get_full_url(request),
            "name": page.seo_title or page.title,
            "isPartOf": {"@id": _abs(request, "/") + "#website"},
        })

    return {"@context": "https://schema.org", "@graph": graph}
