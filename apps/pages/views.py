from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from .forms import ContactForm


class AboutView(TemplateView):
    template_name = "pages/about.html"


class FaqView(TemplateView):
    template_name = "pages/faq.html"


class ContactView(FormView):
    template_name = "pages/contact.html"
    form_class = ContactForm

    def get_success_url(self):
        return reverse("pages:contact")

    def form_valid(self, form):
        data = form.cleaned_data
        # Console email backend — stubbed for the demo.
        send_mail(
            subject="[Pier & Paddock contact] %s"
            % (data.get("subject") or "Website enquiry"),
            message="From: %s <%s>\n\n%s"
            % (data["name"], data["email"], data["message"]),
            from_email=None,
            recipient_list=["concierge@pierandpaddock.example"],
            fail_silently=True,
        )
        messages.success(
            self.request,
            "Thank you — your message has been received. Our concierge team "
            "will be in touch shortly.",
        )
        return super().form_valid(form)


def custom_404(request, exception=None):
    return render(request, "404.html", status=404)
