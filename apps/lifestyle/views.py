"""Plain Django views for the Lifestyle magazine (non-Wagtail surfaces).

Phase 1 ships a stub /advertise/ so the magazine nav/footer links resolve; the
full advertise form + subscription endpoints arrive in Phase 5.
"""
from django.views.generic import TemplateView


class AdvertiseStubView(TemplateView):
    """Phase 1 stub — replaced by the real advertise form in Phase 5."""
    template_name = "lifestyle/advertise.html"
