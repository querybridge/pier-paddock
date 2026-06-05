"""
Django settings for the Pier & Paddock luxury watch demo store.

A django-oscar storefront skinned with the "zwat" theme. This is a sales
demo, not a production site — purchasing is intentionally disabled at the
final checkout step.
"""
import os
from pathlib import Path

from oscar.defaults import *  # noqa: F401,F403  (Oscar's OSCAR_* defaults)
import oscar

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
SECRET_KEY = "demo-insecure-secret-key-not-for-production-pier-and-paddock"
DEBUG = True
ALLOWED_HOSTS = ["*"]

SITE_ID = 1
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# ---------------------------------------------------------------------------
# Brand configuration (demo). Defined once, surfaced everywhere via the
# `apps.core.context_processors.brand` context processor — templates must
# never hardcode these.
# ---------------------------------------------------------------------------
BRAND_NAME = "Pier & Paddock"          # PLACEHOLDER — swap for the real brand
BRAND_TAGLINE = "Time, well spent."
BRAND_FULFILMENT_PARTNER = "International Diamond Center"
BRAND_FOOTER_ATTRIBUTION = "Powered by International Diamond Center"
BRAND_DEMO_DISCLAIMER = "Demo site — transactions are not active."

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "apps.core",  # brand context processor + shared helpers
    *oscar.INSTALLED_APPS,
    "sorl.thumbnail",
    # Local apps (custom apps) appended below.
    "apps.shop.apps.ShopConfig",
    "apps.compare.apps.CompareConfig",
    "apps.vault.apps.VaultConfig",
    "apps.blog.apps.BlogConfig",
    "apps.pages.apps.PagesConfig",
]

# Swap stock Oscar apps for our forked versions. Checkout is forked to disable
# order placement at the payment step (the whole point of the demo). It has no
# models, so the fork needs no migrations.
def _replace_app(installed, original, replacement):
    return [replacement if a == original else a for a in installed]

INSTALLED_APPS = _replace_app(
    INSTALLED_APPS,
    "oscar.apps.checkout.apps.CheckoutConfig",
    "apps.checkout.apps.CheckoutConfig",
)
# Forked shipping app provides two named, insured demo shipping methods.
INSTALLED_APPS = _replace_app(
    INSTALLED_APPS,
    "oscar.apps.shipping.apps.ShippingConfig",
    "apps.shipping.apps.ShippingConfig",
)

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.flatpages.middleware.FlatpageFallbackMiddleware",
    "oscar.apps.basket.middleware.BasketMiddleware",
]

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.request",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.contrib.messages.context_processors.messages",
                "oscar.apps.search.context_processors.search_form",
                "oscar.apps.checkout.context_processors.checkout",
                "oscar.apps.communication.notifications.context_processors.notifications",
                "oscar.core.context_processors.metadata",
                "apps.core.context_processors.brand",
                "apps.core.context_processors.navigation",
                "apps.compare.context_processors.compare",
                "apps.vault.context_processors.vault",
            ],
        },
    },
]

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = (
    "oscar.apps.customer.auth_backends.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
)

LOGIN_REDIRECT_URL = "/"

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "ATOMIC_REQUESTS": True,
    }
}

# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/New_York"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & media
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------------
# Email (console backend for the demo)
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "Pier & Paddock <demo@pierandpaddock.example>"

# ---------------------------------------------------------------------------
# Messages — map to Bootstrap/zwat alert classes
# ---------------------------------------------------------------------------
from django.contrib.messages import constants as message_constants  # noqa: E402

MESSAGE_TAGS = {
    message_constants.DEBUG: "alert-info",
    message_constants.INFO: "alert-info",
    message_constants.SUCCESS: "alert-success",
    message_constants.WARNING: "alert-warning",
    message_constants.ERROR: "alert-danger",
}

# ---------------------------------------------------------------------------
# Oscar
# ---------------------------------------------------------------------------
OSCAR_SHOP_NAME = BRAND_NAME
OSCAR_SHOP_TAGLINE = BRAND_TAGLINE
OSCAR_DEFAULT_CURRENCY = "USD"
OSCAR_PRODUCTS_PER_PAGE = 12
OSCAR_ALLOW_ANON_CHECKOUT = True

# Search — the lightweight in-memory backend is plenty for a demo and needs
# no external service or index rebuild. Faceted shop filtering is handled by
# a custom ORM-based browse view rather than Haystack facets.
HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "haystack.backends.simple_backend.SimpleEngine",
    },
}

# Thumbnails (sorl)
THUMBNAIL_DEBUG = False

# Demo account surfaced in the README / login page.
DEMO_USER_EMAIL = "demo@example.com"
DEMO_USER_PASSWORD = "Demo1234!"
