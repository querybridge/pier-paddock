"""Orchestration for the Crest program.

These functions are the ONLY place spend/credit/tier changes happen, so the
Operator Console demo controls, the (disabled) checkout flow and the seed
command all behave identically. Every spend-changing call ends in
``Membership.recompute()`` and returns enough for the UI to announce a tier
advance ("Patron -> Collector").
"""
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from . import emails
from .models import (
    CreditTransaction,
    DemoPurchase,
    Invitation,
    Membership,
    Notification,
    ProgramConfig,
)

TWOPLACES = Decimal("0.01")


def get_membership(user):
    ms, _ = Membership.objects.get_or_create(user=user)
    return ms


def _q(amount):
    return Decimal(amount).quantize(TWOPLACES)


@transaction.atomic
def record_demo_purchase(user, amount, product=None, note="", accrue_credit=True):
    """Simulate a purchase: log it, add to lifetime spend, accrue Retailer's
    Credit (Collector+), recompute tier. Returns a result dict describing any
    tier advance and credit accrued — the console uses it for the confirmation.
    """
    amount = _q(amount)
    ms = get_membership(user)
    config = ProgramConfig.get()
    old_crest, old_tier = ms.crest_count, ms.tier

    DemoPurchase.objects.create(
        user=user, product=product, amount=amount, note=note or "Simulated purchase",
    )
    ms.lifetime_spend = _q((ms.lifetime_spend or Decimal(0)) + amount)
    ms.purchase_count += 1
    ms.save(update_fields=["lifetime_spend", "purchase_count"])

    # Recompute first so the credit rule sees the post-purchase tier.
    ms.recompute(config)

    credit = Decimal(0)
    if accrue_credit and ms.crest_count >= 3 and config.credit_accrual_rate:
        credit = _q(amount * config.credit_accrual_rate)
        if credit > 0:
            grant_credit(user, credit, note="Retailer's Credit on purchase",
                         type=CreditTransaction.ACCRUED, _recompute=False)
            ms.recalc_credit_balance()

    advanced = ms.crest_count > old_crest
    if advanced:
        notify(user, Notification.PROGRAM,
               title="Membership advanced to %s" % ms.tier,
               body="Your %s crest is now unlocked." % ms.tier)
        emails.send_transactional("tier_advanced", user, {
            "body": "Congratulations — you've advanced to %s (%d crests)."
                    % (ms.tier, ms.crest_count),
        })

    return {
        "amount": amount,
        "credit_accrued": credit,
        "old_tier": old_tier,
        "new_tier": ms.tier,
        "advanced": advanced,
        "old_crest": old_crest,
        "new_crest": ms.crest_count,
        "membership": ms,
    }


@transaction.atomic
def set_lifetime_spend(user, amount):
    """Jump a member's lifetime spend to an exact value (demo convenience) and
    recompute. Does not touch purchase_count or credit."""
    ms = get_membership(user)
    old_tier = ms.tier
    ms.lifetime_spend = _q(amount)
    ms.save(update_fields=["lifetime_spend"])
    ms.recompute()
    return {"old_tier": old_tier, "new_tier": ms.tier,
            "advanced": ms.tier != old_tier, "membership": ms}


@transaction.atomic
def grant_credit(user, amount, note="", type=CreditTransaction.ADJUSTED, _recompute=True):
    """Create a credit movement and refresh the cached balance. ``amount`` may
    be negative (redeem/reduce)."""
    ms = get_membership(user)
    CreditTransaction.objects.create(
        user=user, amount=_q(amount), type=type, note=note,
    )
    if _recompute:
        ms.recalc_credit_balance()
        if _q(amount) > 0:
            notify(user, Notification.PROGRAM,
                   title="Retailer's Credit added",
                   body="$%s in Retailer's Credit is now on your account." % _q(amount))
            emails.send_transactional("credit_granted", user, {
                "body": "We've added $%s in Retailer's Credit to your account."
                        % _q(amount),
            })
    return ms.credit_balance


@transaction.atomic
def issue_invitation(user, issued_by=None, note=""):
    """Invite a member to Steward (sets ``invited`` -> recompute to 5 crests)."""
    ms = get_membership(user)
    old_tier = ms.tier
    Invitation.objects.create(
        email=user.email, user=user, issued_by=issued_by, note=note,
        accepted=True,
    )
    ms.invited = True
    ms.save(update_fields=["invited"])
    ms.recompute()
    notify(user, Notification.PROGRAM,
           title="You've been invited to Steward",
           body="An invitation has elevated your membership to Steward.")
    emails.send_transactional("invitation", user, {
        "body": "You've been personally invited to Pier & Paddock Steward.",
    })
    return {"old_tier": old_tier, "new_tier": ms.tier, "membership": ms}


@transaction.atomic
def mark_grail_matched(grail_entry):
    """Flip a grail entry to matched + notify the member."""
    from .models import GrailEntry

    grail_entry.status = GrailEntry.MATCHED
    grail_entry.save(update_fields=["status"])
    notify(grail_entry.user, Notification.GRAIL_MATCH,
           title="Grail match: %s %s" % (grail_entry.brand, grail_entry.model),
           body="We've located a piece matching your grail entry.")
    emails.send_transactional("grail_matched", grail_entry.user, {
        "body": "Good news — we found a match for %s %s on your grail list."
                % (grail_entry.brand, grail_entry.model),
    })
    return grail_entry


def set_marketing_opt_in(user, opted_in):
    """Toggle marketing opt-in (drives crest 1) and sync to Mailchimp."""
    ms = get_membership(user)
    ms.marketing_opt_in = bool(opted_in)
    ms.save(update_fields=["marketing_opt_in"])
    ms.recompute()
    emails.sync_marketing_contact(user)
    return ms


def notify(user, kind, title, body="", url=""):
    """Append to the member's on-site notification feed."""
    return Notification.objects.create(
        user=user, kind=kind, title=title, body=body, url=url, created=timezone.now(),
    )
