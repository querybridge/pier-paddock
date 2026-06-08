"""Expose the signed-in member's crest state + unread alerts to every template
(used by the header crest chip and the notifications bell)."""


def membership(request):
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return {"membership": None, "loyalty_unread": 0}

    ms = getattr(user, "membership", None)
    if ms is None:
        try:
            from .models import Membership
            ms, _ = Membership.objects.get_or_create(user=user)
        except Exception:
            return {"membership": None, "loyalty_unread": 0}

    unread = 0
    try:
        from .models import Notification
        unread = Notification.objects.filter(user=user, read=False).count()
    except Exception:
        pass

    return {"membership": ms, "loyalty_unread": unread}
