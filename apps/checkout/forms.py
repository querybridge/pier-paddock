"""Forms for the checkout gateway (mandatory registration to purchase)."""
from django import forms
from oscar.apps.customer.forms import EmailUserCreationForm


class CheckoutRegistrationForm(EmailUserCreationForm):
    """Registration at the checkout gateway. Creating an account is mandatory to
    purchase (transaction size); opting into membership communications is not."""

    marketing_opt_in = forms.BooleanField(
        required=False,
        initial=False,
        label="Send me product alerts and Crest membership communications "
              "(you can change this any time).",
    )
