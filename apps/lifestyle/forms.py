"""Forms for the /advertise/ page and newsletter subscriptions."""
from django import forms

from .models import AdvertiseInquiry


class _HoneypotMixin:
    def clean(self):
        cleaned = super().clean()
        if cleaned.get("website"):  # bots fill the hidden field
            raise forms.ValidationError("Submission rejected.")
        return cleaned


class AdvertiseForm(_HoneypotMixin, forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)  # honeypot

    class Meta:
        model = AdvertiseInquiry
        fields = ["name", "company", "email", "phone", "budget", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4, "placeholder": "Tell us about your campaign…"}),
            "name": forms.TextInput(attrs={"placeholder": "Your name"}),
            "company": forms.TextInput(attrs={"placeholder": "Company (optional)"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email"}),
            "phone": forms.TextInput(attrs={"placeholder": "Phone (optional)"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            if not isinstance(f.widget, forms.HiddenInput):
                f.widget.attrs.setdefault("class", "form-control")
        self.fields["company"].required = False
        self.fields["phone"].required = False
        self.fields["budget"].required = False


class SubscribeForm(_HoneypotMixin, forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": "Your email", "class": "form-control"}))
    consent = forms.BooleanField(
        required=True,
        label="I agree to receive P&P Members communications and accept the Privacy Policy.")
    source = forms.CharField(required=False, widget=forms.HiddenInput)
    website = forms.CharField(required=False, widget=forms.HiddenInput)  # honeypot
