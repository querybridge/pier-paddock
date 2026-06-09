from django.contrib import admin

from .models import MerchantProfile


@admin.register(MerchantProfile)
class MerchantProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "partner", "feed_enabled", "last_synced")
    search_fields = ("display_name", "partner__name")
