from django.apps import AppConfig


class MerchantConfig(AppConfig):
    name = "apps.merchant"
    label = "merchant"
    verbose_name = "Merchant Portal"
    default_auto_field = "django.db.models.AutoField"
