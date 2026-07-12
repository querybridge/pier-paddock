"""Phase 6 — AI/crawler discovery endpoints: robots.txt, llms.txt, IndexNow key.

This is a discovery play, not a paywall: major AI crawlers are explicitly allowed.
"""
from django.conf import settings
from django.http import Http404, HttpResponse

from .models import CategoryPage

# Answer-engine / AI crawlers we explicitly welcome.
AI_BOTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-Web",
           "anthropic-ai", "PerplexityBot", "Google-Extended", "Applebot-Extended",
           "CCBot", "Bingbot"]


def robots_txt(request):
    sitemap = request.build_absolute_uri("/sitemap.xml")
    lines = [
        "# Pier & Paddock — storefront + Lifestyle magazine",
        "User-agent: *",
        "Disallow: /cms-admin/",
        "Disallow: /admin/",
        "Disallow: /dashboard/",
        "Disallow: /account/",
        "Disallow: /checkout/",
        "Disallow: /basket/",
        "Allow: /",
        "",
    ]
    for bot in AI_BOTS:  # explicit welcome for answer engines
        lines += ["User-agent: %s" % bot, "Allow: /", ""]
    lines += ["Sitemap: %s" % sitemap, ""]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def llms_txt(request):
    """A concise, LLM-friendly site summary (the emerging llms.txt convention)."""
    base = request.build_absolute_uri("/").rstrip("/")
    cats = CategoryPage.objects.live().public().order_by("path")
    out = [
        "# %s Lifestyle" % settings.BRAND_NAME,
        "",
        "> The online magazine of %s — independent journalism on fine watches, "
        "motorsport, watersports, business, style and the good life. Every story is "
        "editorially independent; sponsored pieces are labelled Partner Content."
        % settings.BRAND_NAME,
        "",
        "## Sections",
    ]
    for c in cats:
        desc = (c.search_description or "").strip()
        out.append("- [%s](%s%s)%s" % (c.title, base, c.url, ": " + desc if desc else ""))
    out += [
        "",
        "## Feeds",
        "- RSS: %s/lifestyle/feed/" % base,
        "- Atom: %s/lifestyle/feed/atom/" % base,
        "",
        "## Also",
        "- Shop (timepieces): %s/" % base,
        "- Advertise: %s/advertise/" % base,
        "- Sitemap: %s/sitemap.xml" % base,
        "",
    ]
    return HttpResponse("\n".join(out), content_type="text/plain; charset=utf-8")


def indexnow_key(request):
    """Serve the IndexNow key verification file at /<key>.txt (only when configured)."""
    key = settings.INDEXNOW_KEY
    if not key:
        raise Http404
    return HttpResponse(key, content_type="text/plain")
