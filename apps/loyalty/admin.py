"""Raw CRUD for every Crest model in Django admin. The Operator Console is the
demo surface, but admin is registered for completeness/back-office editing."""
from django.contrib import admin

from .models import (
    CreditTransaction,
    DemoPurchase,
    EarlyAccessListing,
    GrailEntry,
    Invitation,
    MarketReport,
    Membership,
    Notification,
    ProgramConfig,
)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "tier", "crest_count", "lifetime_spend", "purchase_count",
                    "credit_balance", "marketing_opt_in", "invited", "join_date")
    list_filter = ("tier", "marketing_opt_in", "invited")
    search_fields = ("user__email", "user__username")
    readonly_fields = ("tier", "crest_count", "concierge_channel")


@admin.register(DemoPurchase)
class DemoPurchaseAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "amount", "date", "note")
    search_fields = ("user__email", "product__title")
    list_filter = ("date",)


@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "type", "date", "note")
    list_filter = ("type",)
    search_fields = ("user__email",)


@admin.register(GrailEntry)
class GrailEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "brand", "model", "reference", "target_price", "status")
    list_filter = ("status", "brand")
    search_fields = ("user__email", "brand", "model", "reference")


@admin.register(EarlyAccessListing)
class EarlyAccessListingAdmin(admin.ModelAdmin):
    list_display = ("product", "visible_to_min_crest", "window_start", "window_end")
    list_filter = ("visible_to_min_crest",)


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ("email", "user", "issued_by", "issued_date", "accepted")
    list_filter = ("accepted",)
    search_fields = ("email",)


@admin.register(MarketReport)
class MarketReportAdmin(admin.ModelAdmin):
    list_display = ("quarter_label", "headline", "min_crest", "published")
    list_filter = ("min_crest",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "kind", "title", "created", "read")
    list_filter = ("kind", "read")
    search_fields = ("user__email", "title")


@admin.register(ProgramConfig)
class ProgramConfigAdmin(admin.ModelAdmin):
    list_display = ("__str__", "collector_threshold", "curator_threshold",
                    "steward_threshold", "credit_accrual_rate")

    def has_add_permission(self, request):
        return not ProgramConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
