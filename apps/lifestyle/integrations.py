"""Marketing integration for the Lifestyle magazine — Mailchimp (INACTIVE).

Reads MAILCHIMP_API_KEY / MAILCHIMP_LIST_ID from settings. Until those are set
(and LOYALTY_MARKETING_ENABLED is True), `subscribe()` returns False so the caller
stores a PendingSubscriber locally; `manage.py sync_pending_subscribers` pushes
them once keys exist. Flipping the flag + adding keys activates the live path with
no call-site changes.
"""
import logging

from django.conf import settings

logger = logging.getLogger("lifestyle.mailchimp")


class MailchimpClient:
    def __init__(self):
        self.api_key = getattr(settings, "MAILCHIMP_API_KEY", "")
        self.list_id = getattr(settings, "MAILCHIMP_LIST_ID", "")
        self.server = getattr(settings, "MAILCHIMP_SERVER_PREFIX", "")

    @property
    def enabled(self):
        return bool(
            getattr(settings, "LOYALTY_MARKETING_ENABLED", False)
            and self.api_key and self.list_id
        )

    def subscribe(self, email, source="", merge_fields=None):
        """Upsert a subscriber. Returns True if pushed to Mailchimp, False if the
        integration is disabled (caller should persist locally)."""
        if not self.enabled:
            logger.info("[mailchimp:disabled] would subscribe %s (source=%s)", email, source)
            return False
        return self._upsert(email, source, merge_fields or {})  # pragma: no cover

    def _upsert(self, email, source, merge_fields):  # pragma: no cover - inactive in demo
        """Live path (unimplemented for the demo). Production:

            import hashlib, requests
            sub = hashlib.md5(email.lower().encode()).hexdigest()
            url = f"https://{self.server}.api.mailchimp.com/3.0/lists/{self.list_id}/members/{sub}"
            requests.put(url, auth=("key", self.api_key), json={
                "email_address": email, "status_if_new": "pending",  # double opt-in
                "merge_fields": merge_fields, "tags": [source] if source else [],
            })
        """
        logger.warning("Mailchimp live path not implemented in demo")
        return False
