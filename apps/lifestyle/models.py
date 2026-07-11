"""Pier & Paddock Lifestyle — Wagtail page models.

PHASE 0: only the magazine landing page (LifestyleIndexPage), enough to mount the
Wagtail site at /lifestyle/ and serve a stub. The full information architecture
(CategoryPage, ArticlePage, AuthorPage, StreamField body, etc.) arrives in later
phases per LIFESTYLE_MAGAZINE.md — this model will be extended, not replaced.
"""
from django.db import models
from django.templatetags.static import static
from django.utils.safestring import mark_safe
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.snippets.models import register_snippet


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


class LifestyleIndexPage(Page):
    """The magazine landing page — mounted as the Wagtail site root so its URL is
    /lifestyle/. Laid out to the iNews "Home Page 3" design in a later phase."""

    intro = RichTextField(
        blank=True,
        help_text="Short editorial positioning shown on the landing page.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    # Only one magazine landing page should exist, at the site root.
    max_count = 1

    class Meta:
        verbose_name = "Lifestyle landing page"
