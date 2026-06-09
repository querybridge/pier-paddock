"""Operator Console — the staff-facing demo surface for the Crest program.

A custom, branded-clean dashboard (NOT raw Django admin) at /console/, gated to
staff. The marquee live-demo action is Simulate purchase on a member, which
advances their tier on the spot. All demo controls are clearly labelled and
staff-only. Every state change routes through ``services`` so it behaves exactly
like the real flow would.
"""
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView, View
from oscar.core.loading import get_model

from . import services, tiers
from .models import (
    CreditTransaction,
    EarlyAccessListing,
    GrailEntry,
    Membership,
    ProgramConfig,
)

User = get_user_model()
Product = get_model("catalogue", "Product")


def _decimal(raw, default=None):
    if raw is None or raw == "":
        return default
    try:
        return Decimal(str(raw).replace(",", "").replace("$", "").strip())
    except (InvalidOperation, AttributeError):
        return default


class StaffConsoleMixin(UserPassesTestMixin):
    """Gate every console view to staff users."""
    raise_exception = False

    def test_func(self):
        u = self.request.user
        if not (u.is_authenticated and u.is_staff):
            return False
        # Keep the personas clean: a merchant/listing-partner uses the Merchant
        # Portal, not the loyalty console (superusers see both).
        if not u.is_superuser and self._is_merchant(u):
            return False
        return True

    @staticmethod
    def _is_merchant(user):
        from apps.merchant.models import is_merchant
        return is_merchant(user)

    def handle_no_permission(self):
        messages.error(self.request, "The Operator Console is staff-only.")
        return redirect("/")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["console_section"] = getattr(self, "console_section", "")
        ctx["config"] = ProgramConfig.get()
        return ctx


class DashboardView(StaffConsoleMixin, TemplateView):
    template_name = "console/dashboard.html"
    console_section = "dashboard"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        memberships = Membership.objects.all()

        # Members by tier (ordered down the ladder), with a max for bar widths.
        by_tier = {name: 0 for name in tiers.TIER_NAMES.values()}
        for m in memberships:
            by_tier[m.tier] = by_tier.get(m.tier, 0) + 1
        ladder = [tiers.TIER_NAMES[i] for i in range(1, 6)]
        tier_counts = [{"name": n, "count": by_tier.get(n, 0)} for n in ladder]
        max_count = max([t["count"] for t in tier_counts] + [1])
        for t in tier_counts:
            t["pct"] = round(100 * t["count"] / max_count)

        # Total Retailer's Credit liability outstanding (P&P-funded).
        credit_liability = memberships.aggregate(s=Sum("credit_balance"))["s"] or Decimal(0)

        # Grail demand — most-requested brand/model/reference (the retailer story).
        grail_demand = list(
            GrailEntry.objects.values("brand", "model", "reference")
            .annotate(count=Count("id"))
            .order_by("-count")[:8]
        )

        # Engagement snapshot.
        from apps.vault.models import VaultItem
        ctx.update(
            member_total=memberships.count(),
            tier_counts=tier_counts,
            credit_liability=credit_liability,
            grail_demand=grail_demand,
            vault_saves=VaultItem.objects.count(),
            active_grails=GrailEntry.objects.filter(status=GrailEntry.WATCHING).count(),
            alert_optins=memberships.filter(marketing_opt_in=True).count(),
            steward_count=by_tier.get("Steward", 0),
        )
        return ctx


class MembersView(StaffConsoleMixin, TemplateView):
    template_name = "console/members.html"
    console_section = "members"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = Membership.objects.select_related("user")
        tier = self.request.GET.get("tier")
        if tier:
            qs = qs.filter(tier=tier)
        sort = self.request.GET.get("sort", "-lifetime_spend")
        if sort.lstrip("-") in {"lifetime_spend", "crest_count", "credit_balance", "join_date"}:
            qs = qs.order_by(sort)
        ctx["members"] = qs
        ctx["tier_filter"] = tier or ""
        ctx["sort"] = sort
        ctx["tier_options"] = [tiers.TIER_NAMES[i] for i in range(1, 6)]
        return ctx


class MemberDetailView(StaffConsoleMixin, TemplateView):
    template_name = "console/member_detail.html"
    console_section = "members"

    def _member(self):
        return get_object_or_404(Membership.objects.select_related("user"), pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ms = self._member()
        from apps.vault.models import VaultItem
        ctx.update(
            member=ms,
            user_obj=ms.user,
            vault_items=VaultItem.objects.filter(user=ms.user).select_related("product"),
            grails=ms.user.grail_entries.all(),
            credits=ms.user.credit_transactions.all()[:20],
            purchases=ms.user.demo_purchases.all()[:20],
            watches=Product.objects.browsable().order_by("title")[:200],
            benefits=tiers.benefits_with_state(ms.crest_count),
        )
        return ctx

    def post(self, request, *args, **kwargs):
        ms = self._member()
        user = ms.user
        action = request.POST.get("action")
        back = reverse("console:member", args=[ms.pk])

        if action == "simulate_purchase":
            amount = _decimal(request.POST.get("amount"))
            if not amount or amount <= 0:
                messages.error(request, "Enter a purchase amount.")
                return redirect(back)
            product = None
            pid = request.POST.get("product")
            if pid:
                product = Product.objects.filter(pk=pid).first()
            result = services.record_demo_purchase(
                user, amount, product=product, note="Operator Console — simulated purchase"
            )
            if result["advanced"]:
                messages.success(
                    request,
                    "Tier advanced: %s → %s. $%s spend recorded%s."
                    % (result["old_tier"], result["new_tier"], amount,
                       (", $%s credit accrued" % result["credit_accrued"])
                       if result["credit_accrued"] else ""),
                )
            else:
                messages.success(
                    request,
                    "$%s spend recorded (still %s)%s."
                    % (amount, result["new_tier"],
                       (", $%s credit accrued" % result["credit_accrued"])
                       if result["credit_accrued"] else ""),
                )

        elif action == "set_spend":
            amount = _decimal(request.POST.get("amount"))
            if amount is None or amount < 0:
                messages.error(request, "Enter a valid lifetime spend.")
                return redirect(back)
            result = services.set_lifetime_spend(user, amount)
            messages.success(
                request, "Lifetime spend set to $%s — now %s." % (amount, result["new_tier"])
            )

        elif action == "grant_credit":
            amount = _decimal(request.POST.get("amount"))
            if amount is None or amount == 0:
                messages.error(request, "Enter a credit amount (use a minus sign to deduct).")
                return redirect(back)
            services.grant_credit(user, amount, note="Operator Console adjustment",
                                  type=CreditTransaction.ADJUSTED)
            messages.success(request, "Retailer's Credit adjusted by $%s." % amount)

        elif action == "issue_invitation":
            services.issue_invitation(user, issued_by=request.user,
                                      note="Operator Console invitation")
            messages.success(request, "Invitation issued — %s elevated to Steward." % user.email)

        elif action == "mark_grail":
            entry = GrailEntry.objects.filter(user=user, pk=request.POST.get("grail")).first()
            if entry:
                services.mark_grail_matched(entry)
                messages.success(request, "Grail marked as matched — member notified.")
            else:
                messages.error(request, "Grail entry not found.")

        elif action == "toggle_marketing":
            services.set_marketing_opt_in(user, not ms.marketing_opt_in)
            messages.info(request, "Marketing opt-in toggled.")

        else:
            messages.error(request, "Unknown action.")
        return redirect(back)


class EarlyAccessView(StaffConsoleMixin, TemplateView):
    template_name = "console/early_access.html"
    console_section = "early_access"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["listings"] = EarlyAccessListing.objects.select_related("product")
        ctx["watches"] = Product.objects.browsable().order_by("title")[:200]
        ctx["crest_options"] = [(i, tiers.tier_name(i)) for i in range(2, 6)]
        return ctx

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        if action == "remove":
            EarlyAccessListing.objects.filter(pk=request.POST.get("listing")).delete()
            messages.info(request, "First-look flag removed.")
            return redirect("console:early_access")

        product = Product.objects.filter(pk=request.POST.get("product")).first()
        if not product:
            messages.error(request, "Pick a watch to flag.")
            return redirect("console:early_access")
        try:
            min_crest = int(request.POST.get("min_crest", 4))
        except ValueError:
            min_crest = 4
        days = int(request.POST.get("days") or 3)
        now = timezone.now()
        EarlyAccessListing.objects.create(
            product=product, visible_to_min_crest=min_crest,
            window_start=now, window_end=now + timezone.timedelta(days=days),
        )
        messages.success(
            request,
            "%s flagged as first-look for %s+ (%d days)."
            % (product.title, tiers.tier_name(min_crest), days),
        )
        return redirect("console:early_access")


class ConfigView(StaffConsoleMixin, TemplateView):
    template_name = "console/config.html"
    console_section = "config"

    def post(self, request, *args, **kwargs):
        config = ProgramConfig.get()
        config.collector_threshold = _decimal(
            request.POST.get("collector_threshold"), config.collector_threshold)
        config.curator_threshold = _decimal(
            request.POST.get("curator_threshold"), config.curator_threshold)
        config.steward_threshold = _decimal(
            request.POST.get("steward_threshold"), config.steward_threshold)
        rate = _decimal(request.POST.get("credit_accrual_rate"), config.credit_accrual_rate)
        # Accept either 2 or 0.02 for "2%".
        if rate is not None and rate > 1:
            rate = rate / Decimal(100)
        config.credit_accrual_rate = rate
        config.save()
        # Re-grade every member against the new bands.
        regraded = 0
        for ms in Membership.objects.all():
            before = ms.crest_count
            ms.recompute(config)
            if ms.crest_count != before:
                regraded += 1
        messages.success(
            request,
            "Program configuration saved. %d member(s) re-graded against the new bands."
            % regraded,
        )
        return redirect("console:config")
