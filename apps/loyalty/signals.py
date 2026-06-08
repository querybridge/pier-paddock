"""Keep a Membership profile in lockstep with the user table."""
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Membership


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_membership(sender, instance, created, **kwargs):
    """Every user gets a Crest membership (starts at 0 crests until they opt
    into marketing or make a purchase). Created lazily so existing users and
    the seed command both work."""
    if created:
        Membership.objects.get_or_create(user=instance)
