from decimal import Decimal as D

from oscar.apps.shipping import methods
from oscar.apps.shipping.repository import Repository as CoreRepository


class InsuredOvernight(methods.FixedPrice):
    code = "insured-overnight"
    name = "Insured Overnight — Complimentary"
    description = (
        "Overnight, signature-required and fully insured."
    )
    charge_excl_tax = D("0.00")
    charge_incl_tax = D("0.00")


class SaturdayDelivery(methods.FixedPrice):
    code = "saturday-delivery"
    name = "Saturday Delivery"
    description = (
        "Guaranteed Saturday arrival — fully insured and signature-required."
    )
    charge_excl_tax = D("50.00")
    charge_incl_tax = D("50.00")


class Repository(CoreRepository):
    """Two named, insured shipping options for the demo."""

    methods = (InsuredOvernight(), SaturdayDelivery())

    def get_available_shipping_methods(
        self, basket, shipping_addr=None, **kwargs
    ):
        return self.methods
