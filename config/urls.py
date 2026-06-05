from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.core.views import HomeView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    # Our skinned homepage takes precedence over Oscar's root redirect.
    path("", HomeView.as_view(), name="home"),
    path("shop/", include("apps.shop.urls")),
    path("compare/", include("apps.compare.urls")),
    path("vault/", include("apps.vault.urls")),
    path("blog/", include("apps.blog.urls")),
    path("pages/", include("apps.pages.urls")),
    # Everything else (catalogue, basket, checkout, accounts, search,
    # wishlists, dashboard, ...) comes from Oscar.
    path("", include(apps.get_app_config("oscar").urls[0])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers (skinned 404).
handler404 = "apps.pages.views.custom_404"
