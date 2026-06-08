"""Customer-facing Crest pages — the membership dashboard, grail list, alerts
feed, the public marketing page and the quarterly market report. All member
pages render on the zwat storefront skin via templates/loyalty/account_base.html.
"""
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView, View

from . import services, tiers
from .models import GrailEntry, MarketReport, Notification, ProgramConfig


class _MemberMixin(LoginRequiredMixin):
    """Shared: expose the signed-in member + a flag for the active sub-nav."""
    active_member_tab = ""

    def get_membership(self):
        return services.get_membership(self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ms = self.get_membership()
        ctx["membership"] = ms
        ctx["active_member_tab"] = self.active_member_tab
        ctx["config"] = ProgramConfig.get()
        return ctx


class MembershipDashboardView(_MemberMixin, TemplateView):
    template_name = "loyalty/membership.html"
    active_member_tab = "membership"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ms = ctx["membership"]
        ctx["benefits"] = tiers.benefits_with_state(ms.crest_count)
        ctx["next_step"] = ms.next_threshold(ctx["config"])
        ctx["credit_transactions"] = (
            ms.user.credit_transactions.all()[:6] if ms.has_benefit("retailers_credit") else []
        )
        ctx["notifications"] = ms.user.loyalty_notifications.all()[:5]
        ctx["matched_grails"] = ms.user.grail_entries.filter(status=GrailEntry.MATCHED)
        # Latest report the member is entitled to read (teaser handled in template).
        ctx["latest_report"] = (
            MarketReport.objects.filter(min_crest__lte=ms.crest_count).first()
        )
        ctx["concierge_channel"] = ms.concierge_channel
        return ctx


class GrailListView(_MemberMixin, TemplateView):
    template_name = "loyalty/grail.html"
    active_member_tab = "grail"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ms = ctx["membership"]
        ctx["unlocked"] = ms.has_benefit("grail_list")
        ctx["entries"] = ms.user.grail_entries.all()
        return ctx

    def post(self, request, *args, **kwargs):
        ms = self.get_membership()
        if not ms.has_benefit("grail_list"):
            messages.info(request, "The grail list unlocks at Collector.")
            return redirect("loyalty:grail")
        brand = (request.POST.get("brand") or "").strip()
        model = (request.POST.get("model") or "").strip()
        if not brand or not model:
            messages.error(request, "Please give at least a brand and model.")
            return redirect("loyalty:grail")
        target = request.POST.get("target_price") or ""
        try:
            target_price = Decimal(target.replace(",", "").replace("$", "")) if target else None
        except (InvalidOperation, AttributeError):
            target_price = None
        GrailEntry.objects.create(
            user=request.user, brand=brand, model=model,
            reference=(request.POST.get("reference") or "").strip(),
            target_price=target_price,
        )
        messages.success(request, "Added to your grail list — we'll watch for it.")
        return redirect("loyalty:grail")


class GrailDeleteView(_MemberMixin, View):
    def post(self, request, pk, *args, **kwargs):
        GrailEntry.objects.filter(user=request.user, pk=pk).delete()
        messages.info(request, "Removed from your grail list.")
        return redirect("loyalty:grail")


class AlertsView(_MemberMixin, TemplateView):
    template_name = "loyalty/alerts.html"
    active_member_tab = "alerts"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ms = ctx["membership"]
        ctx["notifications"] = ms.user.loyalty_notifications.all()[:30]
        ctx["on_first_alert"] = ms.has_benefit("first_alert")
        ctx["gets_prelisting"] = ms.has_benefit("first_look_72")
        return ctx

    def post(self, request, *args, **kwargs):
        ms = self.get_membership()
        action = request.POST.get("action")
        if action == "mark_read":
            ms.user.loyalty_notifications.filter(read=False).update(read=True)
            messages.info(request, "Notifications marked as read.")
        else:
            ms.alerts_email = bool(request.POST.get("alerts_email"))
            ms.alerts_sms = bool(request.POST.get("alerts_sms"))
            ms.save(update_fields=["alerts_email", "alerts_sms"])
            from . import emails
            emails.send_transactional("alert_confirmed", request.user)
            messages.success(request, "Your alert preferences were saved.")
        return redirect("loyalty:alerts")


class MarketReportView(_MemberMixin, TemplateView):
    template_name = "loyalty/market_report.html"
    active_member_tab = "membership"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ms = ctx["membership"]
        report = get_object_or_404(MarketReport, pk=kwargs["pk"])
        ctx["report"] = report
        ctx["entitled"] = ms.crest_count >= report.min_crest
        return ctx


class PublicMembershipView(TemplateView):
    """The acquisition surface — explains the five tiers aspirationally. Public."""
    template_name = "loyalty/public_membership.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        config = ProgramConfig.get()
        ctx["config"] = config
        # Build the five-tier marketing table from the single source of truth.
        rows = []
        thresholds = {
            1: "Join + opt in", 2: "First purchase",
            3: "$%s lifetime" % "{:,.0f}".format(config.collector_threshold),
            4: "$%s lifetime" % "{:,.0f}".format(config.curator_threshold),
            5: "$%s lifetime — or by invitation" % "{:,.0f}".format(config.steward_threshold),
        }
        for crest in range(1, 6):
            rows.append({
                "crest": crest,
                "name": tiers.tier_name(crest),
                "earned_by": thresholds[crest],
                "benefits": [b for b in tiers.BENEFITS if b["crest"] == crest],
            })
        ctx["tier_rows"] = rows
        return ctx
