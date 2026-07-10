from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from apps.core.views import HomeView, OperationsLoginView, operations_logout
from apps.loyalty.views import PublicMembershipView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    # Our skinned homepage takes precedence over Oscar's root redirect.
    path("", HomeView.as_view(), name="home"),
    path("shop/", include("apps.shop.urls")),
    path("compare/", include("apps.compare.urls")),
    # Crest membership: customer area + the unified Vault + public page +
    # the staff Operator Console. The Vault is mounted at the top level (not
    # nested under loyalty) so its URL namespace stays 'vault'.
    path("account/vault/", include("apps.vault.urls")),
    path("account/", include("apps.loyalty.urls")),
    path("membership/", PublicMembershipView.as_view(), name="membership_public"),
    # Staff sign-in gateway — routes operators to the console, merchants to the portal.
    path("operations/", OperationsLoginView.as_view(), name="operations"),
    path("operations/logout/", operations_logout, name="operations_logout"),
    path("console/", include("apps.loyalty.console_urls")),
    # Merchant Portal — the supplier/merchant back office (listings, XML feed, sales).
    path("merchant/", include("apps.merchant.urls")),
    # The Vault moved under the member area; keep the old path working.
    path("vault/", RedirectView.as_view(pattern_name="vault:index", permanent=False)),
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
