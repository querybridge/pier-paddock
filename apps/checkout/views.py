from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from oscar.apps.checkout import views as core_views

# Re-export everything from Oscar's checkout views so this module is a complete
# stand-in (get_class('checkout.views', X) resolves against this module).
from oscar.apps.checkout.views import *  # noqa: F401,F403


class PaymentDetailsView(core_views.PaymentDetailsView):
    """Payments are disabled in this demo.

    The customer can walk the entire flow — shipping address, shipping method,
    payment details, and the order preview — but the final "Place order"
    submission never creates an order. Instead we surface a clear notice and,
    if they're signed in, record the watches in their Vault as owned (with the
    price they would have paid) so they can track them as an investment.
    """

    # Flagged in templates to render the disabled card form + notice.
    payments_disabled = True

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["payments_disabled"] = True
        return ctx

    def _add_basket_to_vault(self, request):
        """Simulated post-purchase step: add the basket's watches to the
        signed-in customer's Vault as owned holdings AND record the spend
        against their Crest membership (advancing their tier + accruing
        Retailer's Credit). No real order is created — this is the demo
        stand-in for what a completed purchase would do."""
        if not request.user.is_authenticated:
            return 0
        from apps.vault.models import VaultItem
        from apps.loyalty import services

        added = 0
        today = timezone.now().date()
        for line in request.basket.all_lines():
            product = line.product
            pc = product.get_product_class()
            if pc and pc.name != "Watch":
                continue
            price = line.unit_price_incl_tax or line.unit_price_excl_tax
            if price is None:
                sr = product.stockrecords.first()
                price = sr.price if sr else None
            VaultItem.objects.update_or_create(
                user=request.user, product=product,
                defaults={
                    "status": VaultItem.OWNED,
                    "purchase_price": price,
                    "purchase_date": today,
                },
            )
            # Drive the loyalty program off the (simulated) spend.
            if price is not None:
                services.record_demo_purchase(
                    request.user, price * line.quantity, product=product,
                    note="Demo checkout (no order placed)")
            added += 1
        return added

    def handle_place_order_submission(self, request):
        added = self._add_basket_to_vault(request)
        messages.error(
            request,
            _(
                "Payments are disabled in this demo — no order has been placed "
                "and no card has been charged."
            ),
        )
        if added:
            messages.success(
                request,
                _(
                    "We've added your %(n)d watch(es) to your Vault — track their "
                    "value any time from My Vault."
                )
                % {"n": added},
            )
        elif not request.user.is_authenticated:
            messages.info(
                request,
                _(
                    "Create a free account and your purchases are added to your "
                    "Vault automatically, so you can track them as an investment."
                ),
            )
        return self.render_preview(request)
