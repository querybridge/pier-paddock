"""Push locally-stored PendingSubscribers to Mailchimp once keys are configured.

    python manage.py sync_pending_subscribers

No-op (with a message) while the Mailchimp integration is disabled.
"""
from django.core.management.base import BaseCommand

from apps.lifestyle.integrations import MailchimpClient
from apps.lifestyle.models import PendingSubscriber


class Command(BaseCommand):
    help = "Sync locally-stored newsletter subscribers to Mailchimp."

    def handle(self, *args, **options):
        client = MailchimpClient()
        if not client.enabled:
            self.stdout.write(
                "Mailchimp is not configured (set MAILCHIMP_API_KEY / "
                "MAILCHIMP_LIST_ID and LOYALTY_MARKETING_ENABLED=True). Nothing synced.")
            self.stdout.write("  pending subscribers waiting: %d"
                              % PendingSubscriber.objects.filter(synced=False).count())
            return

        synced = 0
        for sub in PendingSubscriber.objects.filter(synced=False):
            if client.subscribe(sub.email, source=sub.source):
                sub.synced = True
                sub.save(update_fields=["synced"])
                synced += 1
        self.stdout.write(self.style.SUCCESS("Synced %d subscriber(s) to Mailchimp." % synced))
