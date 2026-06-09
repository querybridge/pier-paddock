"""Confine merchant (listing-partner) accounts to the Merchant Portal.

A merchant is a supplier, not a customer: no Crest membership, no customer
account, no storefront. Any path outside the portal (plus sign-out + static)
redirects them to /merchant/. Customers, the loyalty operator, and superusers
are unaffected.
"""
from django.shortcuts import redirect

# Paths a signed-in merchant may reach besides the portal itself.
_ALLOWED_PREFIXES = ("/merchant/", "/static/", "/media/", "/i18n/")


def _allowed(path):
    if any(path.startswith(p) for p in _ALLOWED_PREFIXES):
        return True
    if "logout" in path:          # always let them sign out
        return True
    return False


class MerchantPortalOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        # Only staff non-superusers can be merchants, so skip the DB check for
        # everyone else (customers, anonymous, the loyalty operator's paths that
        # are allowed, superusers).
        if (
            user is not None
            and user.is_authenticated
            and user.is_staff
            and not user.is_superuser
            and not _allowed(request.path)
        ):
            from .models import is_merchant

            if is_merchant(user):
                return redirect("merchant:dashboard")
        return self.get_response(request)
