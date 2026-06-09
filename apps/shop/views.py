from django.core.paginator import Paginator
from django.db.models import Min
from django.views.generic import ListView
from oscar.core.loading import get_model

Product = get_model("catalogue", "Product")
Category = get_model("catalogue", "Category")
ProductAttributeValue = get_model("catalogue", "ProductAttributeValue")

# Attribute codes used for faceted filtering on the shop sidebar.
MATERIAL_CODE = "case_material"
CONDITION_CODE = "condition"

SORT_OPTIONS = {
    "newest": ("-date_created", "Newest"),
    "price-asc": ("min_price", "Price: Low to High"),
    "price-desc": ("-min_price", "Price: High to Low"),
    "title": ("title", "Name: A–Z"),
}


def _distinct_attr_values(code):
    return sorted(
        ProductAttributeValue.objects.filter(attribute__code=code)
        .exclude(value_text="")
        .values_list("value_text", flat=True)
        .distinct()
    )


class ShopView(ListView):
    """Faceted product browse — the main shop page (zwat shop-sidebar)."""

    template_name = "catalogue/browse.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        qs = (
            Product.objects.browsable()
            .filter(structure__in=[Product.STANDALONE, Product.PARENT])
            .annotate(min_price=Min("stockrecords__price"))
            .prefetch_related("images", "stockrecords")
        )
        p = self.request.GET

        brand_slug = p.get("brand")
        if brand_slug:
            qs = qs.filter(categories__slug=brand_slug)

        collection_slug = p.get("collection")
        if collection_slug:
            qs = qs.filter(categories__slug=collection_slug)

        material = p.get("material")
        if material:
            qs = qs.filter(
                attribute_values__attribute__code=MATERIAL_CODE,
                attribute_values__value_text=material,
            )

        condition = p.get("condition")
        if condition:
            qs = qs.filter(
                attribute_values__attribute__code=CONDITION_CODE,
                attribute_values__value_text=condition,
            )

        min_price = _to_decimal(p.get("min_price"))
        if min_price is not None:
            qs = qs.filter(stockrecords__price__gte=min_price)
        max_price = _to_decimal(p.get("max_price"))
        if max_price is not None:
            qs = qs.filter(stockrecords__price__lte=max_price)

        q = p.get("q", "").strip()
        if q:
            from django.db.models import Q

            qs = qs.filter(
                Q(title__icontains=q)
                | Q(attribute_values__value_text__icontains=q)
            )

        sort = p.get("sort", "newest")
        order_field = SORT_OPTIONS.get(sort, SORT_OPTIONS["newest"])[0]
        qs = qs.order_by(order_field, "title")

        return qs.distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        p = self.request.GET

        try:
            brands_root = Category.objects.get(depth=1, slug="brands")
            ctx["brands"] = list(brands_root.get_children())
        except Category.DoesNotExist:
            ctx["brands"] = []
        try:
            collections_root = Category.objects.get(depth=1, slug="collections")
            ctx["collections"] = list(collections_root.get_children())
        except Category.DoesNotExist:
            ctx["collections"] = []

        ctx["materials"] = _distinct_attr_values(MATERIAL_CODE)
        ctx["conditions"] = _distinct_attr_values(CONDITION_CODE)

        ctx["sort_options"] = SORT_OPTIONS
        ctx["current_sort"] = p.get("sort", "newest")
        ctx["selected"] = {
            "brand": p.get("brand", ""),
            "collection": p.get("collection", ""),
            "material": p.get("material", ""),
            "condition": p.get("condition", ""),
            "min_price": p.get("min_price", ""),
            "max_price": p.get("max_price", ""),
            "q": p.get("q", ""),
        }
        # Querystring (minus page) for preserving filters across pagination.
        params = p.copy()
        params.pop("page", None)
        ctx["base_querystring"] = params.urlencode()

        # Heading
        if ctx["selected"]["brand"]:
            match = [b for b in ctx["brands"] if b.slug == ctx["selected"]["brand"]]
            ctx["page_title"] = match[0].name if match else "Shop"
        elif ctx["selected"]["collection"]:
            match = [
                c for c in ctx["collections"] if c.slug == ctx["selected"]["collection"]
            ]
            ctx["page_title"] = match[0].name if match else "Shop"
        elif ctx["selected"]["q"]:
            ctx["page_title"] = 'Search: "%s"' % ctx["selected"]["q"]
        else:
            ctx["page_title"] = "All Watches"

        return ctx


def _to_decimal(value):
    if not value:
        return None
    try:
        from decimal import Decimal

        return Decimal(str(value))
    except (ValueError, ArithmeticError):
        return None


# ---------------------------------------------------------------------------
# AJAX endpoints powering the mini-cart drawer and quick-view modal.
# Both degrade gracefully: without JS the storefront's normal links/forms still
# work (card/PDP forms post to Oscar's basket:add; the quick-view trigger is a
# real link to the product page).
# ---------------------------------------------------------------------------
def _minicart_payload(request):
    from django.template.loader import render_to_string

    basket = request.basket
    total = basket.total_incl_tax if basket.is_tax_known else basket.total_excl_tax
    return {
        "ok": True,
        "num_items": basket.num_items,
        "total": str(total),
        "drawer_html": render_to_string(
            "partials/_minicart_body.html", {"basket": basket}, request=request
        ),
    }


def cart_add(request, pk):
    """Add a watch to the basket; return the mini-cart state as JSON."""
    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404

    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "method"}, status=405)
    product = get_object_or_404(Product, pk=pk)
    try:
        qty = max(1, int(request.POST.get("quantity", 1)))
    except (TypeError, ValueError):
        qty = 1
    sr = product.stockrecords.first()
    if not sr or (sr.num_in_stock or 0) < 1:
        return JsonResponse({"ok": False, "error": "out_of_stock"}, status=400)
    request.basket.add_product(product, quantity=qty)
    payload = _minicart_payload(request)
    payload["added"] = {
        "brand": getattr(product.attr, "brand", ""),
        "model": getattr(product.attr, "model", ""),
    }
    return JsonResponse(payload)


def quick_view(request, pk):
    """Return the quick-view card HTML for a product (modal body)."""
    from django.shortcuts import get_object_or_404, render

    product = get_object_or_404(Product.objects.browsable(), pk=pk)
    return render(request, "partials/_quickview.html", {"product": product})
