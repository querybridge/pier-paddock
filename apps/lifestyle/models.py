"""Pier & Paddock Lifestyle — Wagtail page models.

PHASE 0: only the magazine landing page (LifestyleIndexPage), enough to mount the
Wagtail site at /lifestyle/ and serve a stub. The full information architecture
(CategoryPage, ArticlePage, AuthorPage, StreamField body, etc.) arrives in later
phases per LIFESTYLE_MAGAZINE.md — this model will be extended, not replaced.
"""
import re

from django import forms
from django.core.paginator import Paginator
from django.db import models
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from taggit.models import TaggedItemBase
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Orderable, Page

from .blocks import ArticleBodyBlock
from wagtail.search import index
from wagtail.snippets.models import register_snippet

# Post types the author picks at creation (Phase 3 drives templates/schema off it).
POST_TYPE_CHOICES = [
    ("standard", "Standard Article"),
    ("feature", "Long-form Feature"),
    ("gallery", "Photo Gallery"),
    ("video", "Video Feature"),
    ("audio", "Audio / Podcast"),
    ("quote", "Quote"),
    ("interview", "Interview / Profile"),
    ("review", "Review"),
    ("guide", "Guide / How-To"),
    ("event", "Event Coverage"),
    ("list", "Curated List"),
]


@register_snippet
class AdZone(models.Model):
    """A named ad slot inventoried from the iNews template.

    This is the seam for **Revive Adserver** (Phase 1 stub): the ``{% ad_zone %}``
    tag renders either the local placeholder creative or, when
    ``settings.REVIVE_ENABLED`` and ``revive_tag`` is set, the Revive invocation
    tag. Reserve the exact dimensions in markup (no CLS) — the tag emits
    width/height on the placeholder image.
    """

    slug = models.SlugField(unique=True, help_text="Referenced by {% ad_zone 'slug' %}.")
    name = models.CharField(max_length=80)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    target_url = models.CharField(max_length=300, default="/advertise/",
                                  help_text="Where the placeholder creative links.")
    placeholder_image = models.CharField(
        max_length=200, blank=True,
        help_text="Static path to the placeholder creative (auto-set by lifestyle_ads).")
    revive_tag = models.TextField(
        blank=True,
        help_text="Revive Adserver invocation code. Used instead of the placeholder "
                  "when settings.REVIVE_ENABLED is True.")
    active = models.BooleanField(default=True)

    panels = [
        FieldPanel("slug"), FieldPanel("name"),
        FieldPanel("width"), FieldPanel("height"),
        FieldPanel("target_url"), FieldPanel("placeholder_image"),
        FieldPanel("revive_tag"), FieldPanel("active"),
    ]

    class Meta:
        verbose_name = "Ad zone"
        ordering = ["slug"]

    def __str__(self):
        return "%s (%d×%d)" % (self.name, self.width, self.height)

    def render(self):
        """Return the HTML for this zone (Revive tag or local placeholder)."""
        from django.conf import settings

        if not self.active:
            return ""
        if settings.REVIVE_ENABLED and self.revive_tag:  # pragma: no cover - inactive
            return mark_safe(self.revive_tag)
        src = self.placeholder_image or ""
        if src and not src.startswith(("/", "http")):
            src = static(src)
        return mark_safe(
            '<a class="pp-ad-zone" href="%s" rel="nofollow sponsored" '
            'aria-label="Advertisement"><img src="%s" width="%d" height="%d" '
            'alt="Your Ad Here" loading="lazy"></a>'
            % (self.target_url, src, self.width, self.height)
        )


@register_snippet
class AdvertiseInquiry(models.Model):
    """A submission from the /advertise/ form (also emailed to the ad desk)."""
    BUDGET_CHOICES = [
        ("", "—"),
        ("under_5k", "Under $5,000"),
        ("5_25k", "$5,000 – $25,000"),
        ("25_100k", "$25,000 – $100,000"),
        ("100k_plus", "$100,000+"),
    ]
    name = models.CharField(max_length=120)
    company = models.CharField(max_length=160, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    budget = models.CharField(max_length=20, choices=BUDGET_CHOICES, blank=True)
    message = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    panels = [
        FieldPanel("name"), FieldPanel("company"), FieldPanel("email"),
        FieldPanel("phone"), FieldPanel("budget"), FieldPanel("message"),
    ]

    class Meta:
        ordering = ["-created"]
        verbose_name = "Advertise inquiry"
        verbose_name_plural = "Advertise inquiries"

    def __str__(self):
        return "%s <%s>" % (self.name, self.email)


@register_snippet
class PendingSubscriber(models.Model):
    """A newsletter/Members sign-up stored locally until Mailchimp keys exist.
    Push with `manage.py sync_pending_subscribers`."""
    email = models.EmailField(unique=True)
    source = models.CharField(max_length=120, blank=True, help_text="Page/section it came from.")
    consent = models.BooleanField(default=False)
    synced = models.BooleanField(default=False, help_text="Pushed to Mailchimp.")
    created = models.DateTimeField(auto_now_add=True)

    panels = [
        FieldPanel("email"), FieldPanel("source"),
        FieldPanel("consent"), FieldPanel("synced"),
    ]

    class Meta:
        ordering = ["-created"]
        verbose_name = "Pending subscriber"

    def __str__(self):
        return self.email


@register_snippet
class SponsoredProductSlot(models.Model):
    """A curated sponsored product unit for the article rail's "Sponsored Products"
    section. Mirrors the AdZone pattern: this is the seam for a **Revive**
    product-listing zone (see the ``sponsored_products`` template tag). Falls back
    to the article's related_products / same-category products when no slots exist."""

    product = models.ForeignKey("catalogue.Product", on_delete=models.CASCADE, related_name="+")
    hook = models.CharField(max_length=140, blank=True, help_text="One-line hook.")
    advertiser = models.CharField(max_length=120, blank=True)
    sort_order = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    panels = [
        FieldPanel("product"), FieldPanel("hook"),
        FieldPanel("advertiser"), FieldPanel("sort_order"), FieldPanel("active"),
    ]

    class Meta:
        ordering = ["sort_order"]
        verbose_name = "Sponsored product slot"

    def __str__(self):
        return "%s%s" % (self.product, " (sponsored)" if self.active else "")


class LifestyleIndexPage(Page):
    """The magazine landing page — mounted as the Wagtail site root so its URL is
    /lifestyle/. Renders the iNews "Home Page 3" layout from live content."""

    intro = RichTextField(
        blank=True,
        help_text="Short editorial positioning shown on the landing page.",
    )

    content_panels = Page.content_panels + [FieldPanel("intro")]

    max_count = 1
    subpage_types = ["lifestyle.CategoryPage", "lifestyle.AuthorIndexPage"]

    class Meta:
        verbose_name = "Lifestyle landing page"

    def get_context(self, request):
        ctx = super().get_context(request)
        articles = ArticlePage.objects.live().public().order_by("-first_published_at")
        cats = list(CategoryPage.objects.live().child_of(self).order_by("path"))
        ctx["categories"] = cats
        ctx["featured"] = articles.first()
        ctx["latest"] = articles[1:13]
        # "Trending": most-viewed if we track it cheaply, else most recent fallback.
        ctx["trending"] = articles[:6]
        # Per-category rails (latest 3 in each) for the Home 3 layout.
        ctx["category_rails"] = [
            {"category": c,
             "articles": list(ArticlePage.objects.live().public().child_of(c)
                              .order_by("-first_published_at")[:3])}
            for c in cats
        ]
        return ctx


class CategoryPage(Page):
    """A topical hub (Fashion, Motorsports, …) — the topical-authority page."""

    intro = RichTextField(
        help_text="150–300 words of editorial positioning for this section.")
    hero_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    accent_color = models.CharField(
        max_length=7, blank=True, help_text="Optional hex accent, e.g. #9A7B43.")

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("hero_image"),
        FieldPanel("accent_color"),
        InlinePanel("featured", label="Featured articles", max_num=4),
    ]

    parent_page_types = ["lifestyle.LifestyleIndexPage"]
    subpage_types = ["lifestyle.ArticlePage"]

    class Meta:
        verbose_name = "Category page"

    def get_context(self, request):
        ctx = super().get_context(request)
        qs = (ArticlePage.objects.live().public().child_of(self)
              .order_by("-first_published_at"))
        paginator = Paginator(qs, 9)
        ctx["articles"] = paginator.get_page(request.GET.get("page"))
        ctx["featured_articles"] = [f.article for f in self.featured.all() if f.article]
        return ctx


class CategoryFeatured(Orderable):
    """Manual curation slot: a featured article on a category hub."""
    category = ParentalKey(CategoryPage, on_delete=models.CASCADE, related_name="featured")
    article = models.ForeignKey(
        "lifestyle.ArticlePage", on_delete=models.CASCADE, related_name="+")
    panels = [FieldPanel("article")]


class ArticleTag(TaggedItemBase):
    content_object = ParentalKey("lifestyle.ArticlePage", on_delete=models.CASCADE,
                                 related_name="tagged_items")


class ArticleProduct(Orderable):
    """A shoppable Oscar product related to an article (max 4)."""
    page = ParentalKey("lifestyle.ArticlePage", on_delete=models.CASCADE,
                       related_name="related_products")
    product = models.ForeignKey("catalogue.Product", on_delete=models.CASCADE, related_name="+")
    panels = [FieldPanel("product")]


class ArticleGalleryImage(Orderable):
    """An image in the lead gallery carousel (gallery post type)."""
    page = ParentalKey("lifestyle.ArticlePage", on_delete=models.CASCADE,
                       related_name="gallery_images")
    image = models.ForeignKey("wagtailimages.Image", on_delete=models.CASCADE, related_name="+")
    caption = models.CharField(max_length=255, blank=True)
    panels = [FieldPanel("image"), FieldPanel("caption")]


class ArticlePage(Page):
    """A magazine article. ``post_type`` (required) drives the template variant,
    schema.org type and card badge."""

    post_type = models.CharField(
        max_length=16, choices=POST_TYPE_CHOICES, default="standard",
        help_text="Pick the kind of story — drives layout, schema and badge.")
    subtitle = models.CharField(max_length=255, blank=True, help_text="Dek / standfirst.")

    hero_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    hero_alt_text = models.CharField(
        max_length=255, blank=True, help_text="Required when a hero image is set.")
    hero_caption = models.CharField(max_length=255, blank=True)
    hero_credit = models.CharField(max_length=120, blank=True)

    # Lead media by post type (iNews single-post variants).
    lead_video_url = models.URLField(
        blank=True, help_text="Video post type — YouTube/Vimeo embed URL "
                              "(e.g. https://www.youtube.com/embed/ID).")
    lead_audio_url = models.URLField(
        blank=True, help_text="Audio post type — embed URL (SoundCloud, etc.).")

    authors = ParentalManyToManyField("lifestyle.AuthorPage", blank=True, related_name="articles")
    publish_display_date = models.DateField(null=True, blank=True)
    updated_date = models.DateField(null=True, blank=True)
    reading_time = models.PositiveIntegerField(default=0, help_text="Auto-computed (minutes).")
    tags = ClusterTaggableManager(through=ArticleTag, blank=True)

    is_sponsored = models.BooleanField(
        default=False,
        help_text="Shows a 'Partner Content' disclosure band and marks outbound "
                  "links rel=sponsored.")
    related_articles = ParentalManyToManyField(
        "self", blank=True, symmetrical=False, related_name="+",
        help_text="Manual override; otherwise auto by tag/category.")

    body = StreamField(ArticleBodyBlock(), blank=True)

    # SEO extras (Wagtail already provides seo_title + search_description).
    canonical_url = models.URLField(blank=True)
    og_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    noindex = models.BooleanField(default=False)

    content_panels = Page.content_panels + [
        FieldPanel("post_type"),
        FieldPanel("subtitle"),
        MultiFieldPanel([
            FieldPanel("hero_image"), FieldPanel("hero_alt_text"),
            FieldPanel("hero_caption"), FieldPanel("hero_credit"),
        ], heading="Hero"),
        MultiFieldPanel([
            FieldPanel("lead_video_url"), FieldPanel("lead_audio_url"),
            InlinePanel("gallery_images", label="Gallery images"),
        ], heading="Lead media (video / audio / gallery post types)"),
        FieldPanel("authors", widget=forms.CheckboxSelectMultiple),
        MultiFieldPanel([
            FieldPanel("publish_display_date"), FieldPanel("updated_date"),
            FieldPanel("is_sponsored"),
        ], heading="Meta"),
        FieldPanel("body"),
        FieldPanel("tags"),
        InlinePanel("related_products", label="Shoppable products", max_num=4),
        FieldPanel("related_articles", widget=forms.SelectMultiple),
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel("canonical_url"),
        FieldPanel("og_image"),
        FieldPanel("noindex"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("subtitle"),
        index.SearchField("body"),
        index.FilterField("post_type"),
    ]

    parent_page_types = ["lifestyle.CategoryPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Article"

    # -- Derivations ------------------------------------------------------
    def _plain_body(self):
        return re.sub(r"<[^>]+>", " ", str(self.body))

    def save(self, *args, **kwargs):
        words = len(self._plain_body().split())
        self.reading_time = max(1, round(words / 200)) if words else 1
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.hero_image and not self.hero_alt_text:
            from django.core.exceptions import ValidationError
            raise ValidationError({"hero_alt_text": "Alt text is required when a hero image is set."})

    @property
    def post_type_label(self):
        return dict(POST_TYPE_CHOICES).get(self.post_type, "Article")

    @property
    def category(self):
        parent = self.get_parent().specific
        return parent if isinstance(parent, CategoryPage) else None

    def get_related_articles(self, limit=3):
        manual = list(self.related_articles.live())
        if manual:
            return manual[:limit]
        qs = (ArticlePage.objects.live().public().exclude(id=self.id)
              .filter(tags__in=self.tags.all()).distinct())
        related = list(qs[:limit])
        if len(related) < limit and self.category:
            more = (ArticlePage.objects.live().public().child_of(self.category)
                    .exclude(id=self.id).exclude(id__in=[a.id for a in related]))
            related += list(more[: limit - len(related)])
        return related[:limit]

    def get_context(self, request):
        ctx = super().get_context(request)
        ctx["related"] = self.get_related_articles()
        return ctx


class AuthorIndexPage(Page):
    """Listing of magazine authors (/lifestyle/authors/)."""
    intro = RichTextField(blank=True)
    content_panels = Page.content_panels + [FieldPanel("intro")]
    max_count = 1
    parent_page_types = ["lifestyle.LifestyleIndexPage"]
    subpage_types = ["lifestyle.AuthorPage"]

    class Meta:
        verbose_name = "Authors index"

    def get_context(self, request):
        ctx = super().get_context(request)
        ctx["authors"] = AuthorPage.objects.live().child_of(self).order_by("title")
        return ctx


class AuthorPage(Page):
    """A bylined author — real bio + credentials for E-E-A-T."""
    portrait = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    role = models.CharField(max_length=120, blank=True, help_text="Title / credentials.")
    bio = RichTextField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    website = models.URLField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("portrait"),
        FieldPanel("role"),
        FieldPanel("bio"),
        MultiFieldPanel([
            FieldPanel("twitter"), FieldPanel("instagram"),
            FieldPanel("linkedin"), FieldPanel("website"),
        ], heading="Social / sameAs"),
    ]

    parent_page_types = ["lifestyle.AuthorIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Author"

    def get_context(self, request):
        ctx = super().get_context(request)
        qs = self.articles.live().public().order_by("-first_published_at")
        ctx["articles"] = Paginator(qs, 9).get_page(request.GET.get("page"))
        return ctx
