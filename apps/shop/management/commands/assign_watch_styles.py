"""Create the watch 'style' option attribute and populate it for existing products.

Idempotent: creates the AttributeOptionGroup + options + the 'style' ProductAttribute,
then assigns a style (auto-classified from the title) to any Watch product that doesn't
already have one — preserving styles set manually in the dashboard. The catalogue loader
does this automatically on a full rebuild; this command is for the already-seeded db.
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the 'style' option attribute and classify existing watches."

    def handle(self, *args, **options):
        from oscar.core.loading import get_model
        from apps.shop.watch_styles import (
            classify, ensure_style_attribute, set_product_style,
        )

        Product = get_model("catalogue", "Product")
        ProductClass = get_model("catalogue", "ProductClass")

        ensure_style_attribute()
        pc = ProductClass.objects.get(name="Watch")
        assigned = 0
        for p in Product.objects.filter(product_class=pc):
            try:
                if getattr(getattr(p.attr, "style", None), "code", None):
                    continue  # already has a style — leave it
            except Exception:
                pass
            set_product_style(p, classify(p.title))
            assigned += 1
        self.stdout.write(self.style.SUCCESS(
            "Style attribute ready; assigned to %d product(s)." % assigned))
