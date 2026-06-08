"""Email integration for the Crest program — structured for two providers but
INACTIVE in the demo.

    * Transactional  -> SendGrid   (per-event mail: tier advances, grail
                                     matches, alert confirmations, concierge.)
    * Marketing       -> Mailchimp  (audience sync + broadcast: newsletter,
                                     quarterly market report.)

Nothing here makes a network call while the corresponding
``LOYALTY_*_ENABLED`` setting is False (the default). Disabled transactional
sends fall back to Django's console email backend so you can SEE them in the
runserver log during the demo; disabled marketing syncs just log what WOULD be
posted to Mailchimp. Real keys + flipping the settings flag activate the live
path without changing a single call site.

Call sites use the three public helpers at the bottom:
    send_transactional(event, user, context=None)
    sync_marketing_contact(user)
    broadcast_marketing(subject, html, min_crest=1)
"""
import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger("loyalty.emails")

# Transactional event -> default subject line. Bodies are simple here; a real
# build would map these to SendGrid dynamic templates by id.
TRANSACTIONAL_EVENTS = {
    "tier_advanced": "Your Pier & Paddock membership has advanced",
    "grail_matched": "We found a match on your grail list",
    "credit_granted": "Retailer's Credit added to your account",
    "first_look": "A members-only first look is in your Vault",
    "invitation": "An invitation to Pier & Paddock Steward",
    "alert_confirmed": "Your alert preferences were updated",
}


# ---------------------------------------------------------------------------
# Transactional (SendGrid)
# ---------------------------------------------------------------------------
def send_transactional(event, user, context=None):
    """Send a per-event transactional email.

    Live path (LOYALTY_TRANSACTIONAL_ENABLED + SENDGRID_API_KEY): would POST to
    the SendGrid v3 mail/send endpoint using the dynamic template mapped to
    ``event``. Demo path: render a plain message and hand it to Django's
    configured (console) email backend so it shows in the log.
    """
    context = context or {}
    to = getattr(user, "email", None)
    if not to:
        return False
    subject = context.get("subject") or TRANSACTIONAL_EVENTS.get(
        event, "A note from Pier & Paddock"
    )
    body = context.get("body") or subject

    if settings.LOYALTY_TRANSACTIONAL_ENABLED and settings.SENDGRID_API_KEY:
        # PRODUCTION: dispatch via SendGrid. Intentionally not wired in the demo.
        return _sendgrid_send(event, to, subject, body, context)

    # DEMO: route through the console backend (no external call).
    logger.info("[transactional:disabled] event=%s to=%s -> console backend", event, to)
    msg = EmailMultiAlternatives(
        subject=subject, body=body,
        from_email=settings.SENDGRID_FROM_EMAIL, to=[to],
    )
    try:
        msg.send(fail_silently=True)
    except Exception:  # pragma: no cover - demo console backend won't raise
        pass
    return True


def _sendgrid_send(event, to, subject, body, context):  # pragma: no cover - inactive in demo
    """Live SendGrid dispatch. Left unimplemented on purpose for the demo —
    flip LOYALTY_TRANSACTIONAL_ENABLED and add the official ``sendgrid`` client:

        import sendgrid
        from sendgrid.helpers.mail import Mail
        sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
        mail = Mail(from_email=settings.SENDGRID_FROM_EMAIL, to_emails=to)
        mail.template_id = SENDGRID_TEMPLATE_IDS[event]
        mail.dynamic_template_data = context
        sg.send(mail)
    """
    logger.warning("SendGrid live path not implemented in demo (event=%s)", event)
    return False


# ---------------------------------------------------------------------------
# Marketing (Mailchimp)
# ---------------------------------------------------------------------------
def sync_marketing_contact(user):
    """Upsert the member into the Mailchimp audience with their tier as a merge
    field / segment tag, IF they've opted in. No-op (logged) while disabled."""
    ms = getattr(user, "membership", None)
    if ms is None or not ms.marketing_opt_in:
        return False

    payload = {
        "email_address": user.email,
        "status": "subscribed",
        "merge_fields": {"TIER": ms.tier, "CRESTS": ms.crest_count},
        "tags": [ms.tier],
    }

    if settings.LOYALTY_MARKETING_ENABLED and settings.MAILCHIMP_API_KEY:
        return _mailchimp_upsert(payload)  # pragma: no cover - inactive in demo

    logger.info("[marketing:disabled] would sync %s to Mailchimp: %s", user.email, payload)
    return True


def broadcast_marketing(subject, html, min_crest=1):
    """Create + (would) send a Mailchimp campaign to members at/above a crest
    level. No-op (logged) while disabled."""
    if settings.LOYALTY_MARKETING_ENABLED and settings.MAILCHIMP_API_KEY:
        return _mailchimp_campaign(subject, html, min_crest)  # pragma: no cover

    logger.info("[marketing:disabled] would broadcast '%s' to crest>=%d", subject, min_crest)
    return True


def _mailchimp_upsert(payload):  # pragma: no cover - inactive in demo
    """Live Mailchimp member upsert. Unimplemented for the demo; production:

        import hashlib, requests
        sub = hashlib.md5(payload['email_address'].lower().encode()).hexdigest()
        url = f"https://{settings.MAILCHIMP_SERVER_PREFIX}.api.mailchimp.com/3.0/" \
              f"lists/{settings.MAILCHIMP_AUDIENCE_ID}/members/{sub}"
        requests.put(url, auth=("key", settings.MAILCHIMP_API_KEY), json=payload)
    """
    logger.warning("Mailchimp live path not implemented in demo")
    return False


def _mailchimp_campaign(subject, html, min_crest):  # pragma: no cover - inactive in demo
    logger.warning("Mailchimp campaign live path not implemented in demo")
    return False
