from django.views.generic import TemplateView
from oscar.core.loading import get_model

Product = get_model("catalogue", "Product")
Category = get_model("catalogue", "Category")


class HomeView(TemplateView):
    """Skinned homepage (zwat 'Home Page 3')."""

    template_name = "home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        browsable = (
            Product.objects.browsable()
            .filter(structure__in=[Product.STANDALONE, Product.PARENT])
            .order_by("-date_created")
        )

        ctx["new_arrivals"] = list(browsable[:8])
        # "Featured" — a stable but distinct slice for the carousel.
        ctx["featured_products"] = list(browsable.order_by("title")[:8])

        # Top-level brand/style categories for the collection blocks.
        ctx["collections"] = list(Category.get_root_nodes()[:6])

        try:
            from apps.blog.models import Post

            ctx["latest_posts"] = list(
                Post.objects.filter(published=True).order_by("-date")[:3]
            )
        except Exception:
            ctx["latest_posts"] = []

        return ctx
