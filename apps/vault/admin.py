from django.contrib import admin

from .models import MarketValue, VaultItem


@admin.register(MarketValue)
class MarketValueAdmin(admin.ModelAdmin):
    list_display = ("product", "value", "currency", "updated")
    search_fields = ("product__title",)


@admin.register(VaultItem)
class VaultItemAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "status", "purchase_price", "purchase_date", "added")
    list_filter = ("status",)
    search_fields = ("user__email", "product__title")
