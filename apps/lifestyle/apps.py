from django.apps import AppConfig


class LifestyleConfig(AppConfig):
    name = "apps.lifestyle"
    label = "lifestyle"
    verbose_name = "Pier & Paddock Lifestyle"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        from . import signals  # noqa: F401  (IndexNow ping on publish)
