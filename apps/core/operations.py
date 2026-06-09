"""Operations sign-in routing — where staff go to log in, and where they land.

Operators (Pier & Paddock staff / superusers) belong in the Operator Console;
merchants (listing partners) belong in the Merchant Portal. The Operations login
page (apps.core.views.OperationsLoginView) and the two back-office access gates
share this logic so a staff user is always routed to the right surface.
"""
from django.shortcuts import redirect
from django.urls import reverse


def operations_home_url(user):
    """The back-office URL a signed-in user belongs to, or None if they're not
    an operations user (e.g. an anonymous visitor or a customer)."""
    if user is None or not getattr(user, "is_authenticated", False):
        return None
    from apps.merchant.models import is_merchant

    if is_merchant(user):
        return reverse("merchant:dashboard")
    if user.is_staff:                      # operator or superuser
        return reverse("console:dashboard")
    return None


def route_to_operations(request, next_path=None):
    """Decide where to send someone who hit a staff-only page they can't view:

    - signed-in staff  -> their own back-office (operator -> console, merchant
      -> portal);
    - everyone else (anonymous or a customer) -> the Operations login page,
      carrying ?next so they return to the page they wanted after signing in.
    """
    home = operations_home_url(getattr(request, "user", None))
    if home:
        return redirect(home)
    login_url = reverse("operations")
    if next_path:
        login_url = "%s?next=%s" % (login_url, next_path)
    return redirect(login_url)
