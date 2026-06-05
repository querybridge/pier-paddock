from oscar.core.loading import get_model

from .views import SESSION_KEY


def compare(request):
    """Expose the compare list to templates.

    The count reflects only products that still exist — stale IDs (e.g. left
    over from a re-seed) are pruned so the badge can't show phantom entries.
    """
    session = getattr(request, "session", None)
    ids = list(session.get(SESSION_KEY, [])) if session is not None else []

    if ids:
        Product = get_model("catalogue", "Product")
        existing = set(
            Product.objects.filter(id__in=ids).values_list("id", flat=True)
        )
        valid = [i for i in ids if i in existing]
        if len(valid) != len(ids):
            session[SESSION_KEY] = valid
            session.modified = True
        ids = valid

    return {"compare_count": len(ids), "compare_ids": ids}
