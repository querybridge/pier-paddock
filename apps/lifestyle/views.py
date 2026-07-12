"""Plain Django views for the Lifestyle magazine (non-Wagtail surfaces).

Phase 5: the /advertise/ enquiry form and the newsletter/Members subscribe
endpoint (Mailchimp-pending — stores locally + ties into the Crest program).
"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import FormView

from .forms import AdvertiseForm, SubscribeForm
from .integrations import MailchimpClient
from .models import ArticlePage, PendingSubscriber


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    return (xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR", "")) or "?"


class AdvertiseView(FormView):
    """The magazine advertise page — positioning + enquiry form. On submit: emails
    the ad desk (console backend in dev), stores an AdvertiseInquiry, confirms.
    Honeypot (on the form) + light per-IP rate limiting."""

    template_name = "lifestyle/advertise.html"
    form_class = AdvertiseForm

    def get_success_url(self):
        return reverse("advertise") + "?sent=1"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["sent"] = self.request.GET.get("sent") == "1"
        return ctx

    def post(self, request, *args, **kwargs):
        key = "ppl-advertise-rl:%s" % _client_ip(request)
        if cache.get(key, 0) >= 5:  # 5 submissions / hour / IP
            form = self.get_form()
            form.add_error(None, "Too many submissions. Please try again later.")
            return self.form_invalid(form)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        inquiry = form.save()
        key = "ppl-advertise-rl:%s" % _client_ip(self.request)
        cache.set(key, cache.get(key, 0) + 1, 3600)
        send_mail(
            subject="[Lifestyle · Advertise] %s%s" % (inquiry.name, " · %s" % inquiry.company if inquiry.company else ""),
            message="Name: %s\nCompany: %s\nEmail: %s\nPhone: %s\nBudget: %s\n\n%s" % (
                inquiry.name, inquiry.company, inquiry.email, inquiry.phone,
                inquiry.get_budget_display(), inquiry.message),
            from_email=None,
            recipient_list=["advertise@pierandpaddock.com"],
            fail_silently=True,
        )
        return super().form_valid(form)


def subscribe(request):
    """Single endpoint for every newsletter/Members form (footer, sidebar, inline).

    Mailchimp-pending: if the integration is disabled, store a PendingSubscriber.
    Crest tie-in: subscribing = eligibility for Member (1 crest). If the email
    matches a store account, opt them into membership comms now; otherwise the
    PendingSubscriber records the intent for account creation to link later.
    """
    back = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/lifestyle/"

    def _redir(status):
        sep = "&" if "?" in back else "?"
        return redirect("%s%ssubscribed=%s" % (back, sep, status))

    if request.method != "POST":
        return redirect("/lifestyle/")

    form = SubscribeForm(request.POST)
    if not form.is_valid():
        return _redir("err")

    email = form.cleaned_data["email"]
    source = form.cleaned_data.get("source", "")
    consent = form.cleaned_data["consent"]

    if not MailchimpClient().subscribe(email, source=source):
        PendingSubscriber.objects.update_or_create(
            email=email, defaults={"source": source, "consent": consent})

    # Crest tie-in — existing account → Member (1 crest); else intent is stored.
    user = get_user_model().objects.filter(email__iexact=email).first()
    if user is not None:
        try:
            from apps.loyalty.models import Membership  # merchants have none
            if Membership.objects.filter(user=user).exists() or not user.is_staff:
                from apps.loyalty import services
                services.set_marketing_opt_in(user, True)
        except Exception:
            pass

    return _redir("1")


def magazine_search(request):
    """Phase 7 — magazine search over live ArticlePages.

    Uses a plain substring query across title/subtitle/body/tags rather than the
    Wagtail DB backend, which under-matches on SQLite (a term users expect to hit
    would return nothing). Predictable is better UX for the demo.
    """
    from django.db.models import Q

    query = (request.GET.get("q") or "").strip()
    qs = ArticlePage.objects.none()
    if query:
        qs = (ArticlePage.objects.live().public()
              .filter(Q(title__icontains=query) | Q(subtitle__icontains=query)
                      | Q(body__icontains=query) | Q(tags__name__icontains=query))
              .distinct().order_by("-first_published_at"))
    page = Paginator(qs, 9).get_page(request.GET.get("page"))
    return render(request, "lifestyle/search.html", {"query": query, "results": page})
