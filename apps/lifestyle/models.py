"""Pier & Paddock Lifestyle — Wagtail page models.

PHASE 0: only the magazine landing page (LifestyleIndexPage), enough to mount the
Wagtail site at /lifestyle/ and serve a stub. The full information architecture
(CategoryPage, ArticlePage, AuthorPage, StreamField body, etc.) arrives in later
phases per LIFESTYLE_MAGAZINE.md — this model will be extended, not replaced.
"""
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


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
