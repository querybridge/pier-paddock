"""Create the Lifestyle magazine site root and mount it at /lifestyle/.

Idempotent: safe to run on every deploy. Creates a single LifestyleIndexPage
under the Wagtail tree root and points the default Wagtail Site at it, so the
magazine serves at /lifestyle/ (wagtail_urls is included under that prefix in
config/urls.py). Later phases add categories/articles under this page.
"""
from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from apps.lifestyle.models import LifestyleIndexPage


class Command(BaseCommand):
    help = "Set up the Lifestyle magazine site root (idempotent)."

    def handle(self, *args, **options):
        root = Page.get_first_root_node()

        index = LifestyleIndexPage.objects.first()
        if index is None:
            index = LifestyleIndexPage(
                title="Pier & Paddock Lifestyle",
                slug="lifestyle-home",
                intro="",
            )
            root.add_child(instance=index)
            index.save_revision().publish()
            self.stdout.write("  created LifestyleIndexPage")
        else:
            self.stdout.write("  LifestyleIndexPage already exists")

        site = Site.objects.filter(is_default_site=True).first()
        if site is None:
            site = Site.objects.create(
                hostname="localhost", port=80, is_default_site=True,
                root_page=index, site_name="Pier & Paddock Lifestyle",
            )
            self.stdout.write("  created default Site -> LifestyleIndexPage")
        else:
            old = site.root_page
            site.root_page = index
            site.site_name = "Pier & Paddock Lifestyle"
            site.save()
            # Clean up Wagtail's default "Welcome" home page if it was the root.
            if old and old.id != index.id and old.depth > 1:
                try:
                    old.delete()
                except Exception:
                    pass
            self.stdout.write("  default Site now roots at LifestyleIndexPage")

        self.stdout.write(self.style.SUCCESS("Lifestyle site root ready at /lifestyle/"))
