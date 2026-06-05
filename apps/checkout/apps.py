from oscar.apps.checkout.apps import CheckoutConfig as CoreCheckoutConfig


class CheckoutConfig(CoreCheckoutConfig):
    """Forked checkout app.

    Identity (label/namespace) is inherited from Oscar; only the Python path
    changes so that ``get_class('checkout.views', ...)`` resolves to our
    overridden views (notably the payments-disabled PaymentDetailsView).
    """

    name = "apps.checkout"
