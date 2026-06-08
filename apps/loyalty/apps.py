from django.apps import AppConfig


class LoyaltyConfig(AppConfig):
    name = "apps.loyalty"
    label = "loyalty"
    verbose_name = "Crest Membership"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        # Register signal handlers (auto-create a Membership for every user).
        from . import signals  # noqa: F401
