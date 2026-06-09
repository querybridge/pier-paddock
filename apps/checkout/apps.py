from oscar.apps.checkout.apps import CheckoutConfig as CoreCheckoutConfig


class CheckoutConfig(CoreCheckoutConfig):
    """Forked checkout app.

    Identity (label/namespace) is inherited from Oscar; only the Python path
    changes so that ``get_class('checkout.views', ...)`` resolves to our
    overridden views (notably the payments-disabled PaymentDetailsView).
    """

    name = "apps.checkout"

    def get_url_decorator(self, pattern):
        # Registration is mandatory to purchase (OSCAR_ALLOW_ANON_CHECKOUT=False),
        # which makes Oscar wrap EVERY checkout view in login_required. Exempt the
        # gateway (index) so anonymous shoppers can reach our custom Log In /
        # Register page; every later step stays login-required.
        if pattern.name == "index":
            return None
        return super().get_url_decorator(pattern)
