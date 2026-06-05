from django.conf import settings


def navigation(request):
    """Brand + collection categories for the primary nav, plus live counts."""
    brands, collections = [], []
    try:
        from oscar.core.loading import get_model

        Category = get_model("catalogue", "Category")
        try:
            brands = list(Category.objects.get(depth=1, slug="brands").get_children())
        except Category.DoesNotExist:
            brands = []
        try:
            collections = list(
                Category.objects.get(depth=1, slug="collections").get_children()
            )
        except Category.DoesNotExist:
            collections = []
    except Exception:
        pass

    wishlist_count = 0
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        try:
            from oscar.core.loading import get_model

            WishList = get_model("wishlists", "WishList")
            wishlist_count = sum(
                wl.lines.count() for wl in WishList.objects.filter(owner=user)
            )
        except Exception:
            wishlist_count = 0

    return {
        "nav_brands": brands,
        "nav_collections": collections,
        "wishlist_count": wishlist_count,
    }


def brand(request):
    """Expose brand configuration to every template.

    Templates must never hardcode brand strings — they pull from here.
    """
    return {
        "BRAND_NAME": settings.BRAND_NAME,
        "BRAND_TAGLINE": settings.BRAND_TAGLINE,
        "BRAND_FULFILMENT_PARTNER": settings.BRAND_FULFILMENT_PARTNER,
        "BRAND_FOOTER_ATTRIBUTION": settings.BRAND_FOOTER_ATTRIBUTION,
        "BRAND_DEMO_DISCLAIMER": settings.BRAND_DEMO_DISCLAIMER,
        "DEMO_USER_EMAIL": settings.DEMO_USER_EMAIL,
    }
