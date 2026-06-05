def vault(request):
    """Expose the current user's vault count + product ids to templates."""
    count, ids = 0, []
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        try:
            from .models import VaultItem

            ids = list(
                VaultItem.objects.filter(user=user).values_list("product_id", flat=True)
            )
            count = len(ids)
        except Exception:
            pass
    return {"vault_count": count, "vault_product_ids": ids}
