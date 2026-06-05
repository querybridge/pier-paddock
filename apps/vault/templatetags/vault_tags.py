from django import template

register = template.Library()


@register.filter
def market_value(product):
    """Latest (current) market value for a product, or None."""
    mv = getattr(product, "market_value", None)
    return mv.value if mv else None


@register.filter
def vault_saves(product):
    """How many collectors have this watch in their Vault (social proof)."""
    from apps.vault.models import VaultItem

    try:
        return VaultItem.objects.filter(product=product).count()
    except Exception:
        return 0
