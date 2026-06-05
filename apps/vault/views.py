from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView
from oscar.core.loading import get_model

from .models import VaultItem

Product = get_model("catalogue", "Product")


def _is_watch(product):
    pc = product.get_product_class()
    return pc is None or pc.name == "Watch"


@login_required
def add(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if not _is_watch(product):
        messages.info(request, "Only watches can be added to the Vault.")
        return redirect(product.get_absolute_url())
    item, created = VaultItem.objects.get_or_create(
        user=request.user, product=product,
        defaults={"status": VaultItem.WATCHING},
    )
    if created:
        messages.success(request, "Added to your Vault — now tracking its value.")
    else:
        messages.info(request, "This watch is already in your Vault.")
    return redirect("vault:index")


@login_required
def remove(request, pk):
    VaultItem.objects.filter(user=request.user, product_id=pk).delete()
    messages.info(request, "Removed from your Vault.")
    return redirect("vault:index")


@login_required
def mark_owned(request, pk):
    """Move a watched item into the owned collection, recording a purchase
    price (defaults to the listed price if none is supplied)."""
    item = get_object_or_404(VaultItem, user=request.user, product_id=pk)

    price = request.GET.get("price") or request.POST.get("price")
    if price:
        try:
            price = Decimal(str(price).replace(",", "").replace("$", "").strip())
        except Exception:
            price = None
    if not price:
        sr = item.product.stockrecords.first()
        price = sr.price if sr else item.latest_value

    from django.utils import timezone

    item.status = VaultItem.OWNED
    item.purchase_price = price
    item.purchase_date = timezone.now().date()
    item.save()
    messages.success(request, "Added to your owned collection.")
    return redirect("vault:index")


class VaultView(LoginRequiredMixin, TemplateView):
    template_name = "vault/vault.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        items = list(
            VaultItem.objects.filter(user=self.request.user)
            .select_related("product", "product__market_value")
            .prefetch_related("product__images", "product__attribute_values__attribute")
        )
        owned = [i for i in items if i.owned]
        watching = [i for i in items if not i.owned]

        total_cost = sum((i.purchase_price or Decimal(0)) for i in owned)
        total_value = sum(
            (i.latest_value or i.purchase_price or Decimal(0)) for i in owned
        )
        total_gain = total_value - total_cost
        total_pct = (total_gain / total_cost * Decimal(100)) if total_cost else None

        ctx.update(
            owned=owned,
            watching=watching,
            total_cost=total_cost,
            total_value=total_value,
            total_gain=total_gain,
            total_pct=total_pct,
        )
        return ctx
