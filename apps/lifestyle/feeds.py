"""Phase 6 — RSS/Atom syndication feeds for the Lifestyle magazine.

`/lifestyle/feed/` (RSS) + `/lifestyle/feed/atom/` (Atom) + per-category
`/lifestyle/<category>/feed/`. Absolute URLs are built from the request so they're
correct regardless of the django.contrib.sites domain.
"""
from django.contrib.syndication.views import Feed
from django.http import Http404
from django.utils.feedgenerator import Atom1Feed, Enclosure

from .models import ArticlePage, CategoryPage


class LatestArticlesFeed(Feed):
    title = "Pier & Paddock Lifestyle"
    description = "The latest stories from Pier & Paddock Lifestyle — watches, motorsport, style and the good life."

    def __call__(self, request, *args, **kwargs):
        self.request = request  # stash for absolute URLs in item_* methods
        return super().__call__(request, *args, **kwargs)

    def _abs(self, url):
        return self.request.build_absolute_uri(url) if url else ""

    def link(self):
        return self._abs("/lifestyle/")

    def items(self):
        return ArticlePage.objects.live().public().order_by("-first_published_at")[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.search_description or item.subtitle or ""

    def item_link(self, item):
        return self._abs(item.url)

    def item_pubdate(self, item):
        return item.first_published_at

    def item_updateddate(self, item):
        return item.last_published_at or item.first_published_at

    def item_author_name(self, item):
        a = item.authors.first()
        return a.title if a else None

    def item_categories(self, item):
        cats = [item.category.title] if item.category else []
        return cats + [t.name for t in item.tags.all()]

    def item_enclosures(self, item):
        img = item.og_image or item.hero_image
        if not img:
            return []
        try:
            r = img.get_rendition("width-1200")
            return [Enclosure(self._abs(r.url), str(r.file.size), "image/webp")]
        except Exception:
            return []


class LatestArticlesAtomFeed(LatestArticlesFeed):
    feed_type = Atom1Feed
    subtitle = LatestArticlesFeed.description


class CategoryFeed(LatestArticlesFeed):
    """Per-category feed at /lifestyle/<category>/feed/."""

    def get_object(self, request, category):
        page = CategoryPage.objects.live().filter(slug=category).first()
        if not page:
            raise Http404("No such category")
        return page

    def title(self, obj):
        return "Pier & Paddock Lifestyle — %s" % obj.title

    def link(self, obj):
        return self._abs(obj.url)

    def description(self, obj):
        return "Latest %s stories from Pier & Paddock Lifestyle." % obj.title

    def items(self, obj):
        return (ArticlePage.objects.live().public().child_of(obj)
                .order_by("-first_published_at")[:20])
