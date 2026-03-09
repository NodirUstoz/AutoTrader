"""
Admin configuration for the listings app.
"""

from django.contrib import admin

from .models import Listing, PriceHistory, SavedSearch


class PriceHistoryInline(admin.TabularInline):
    model = PriceHistory
    extra = 0
    readonly_fields = ("price", "changed_at", "note")


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "vehicle",
        "price",
        "status",
        "is_featured",
        "views_count",
        "saves_count",
        "city",
        "state",
        "published_at",
        "created_at",
    )
    list_filter = ("status", "is_featured", "is_negotiable", "state")
    search_fields = (
        "vehicle__make__name",
        "vehicle__model__name",
        "seller__email",
        "city",
    )
    readonly_fields = ("views_count", "saves_count", "inquiries_count", "created_at", "updated_at")
    inlines = [PriceHistoryInline]
    raw_id_fields = ("vehicle", "seller")

    actions = ["make_featured", "remove_featured"]

    @admin.action(description="Mark selected listings as featured")
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description="Remove featured status from selected listings")
    def remove_featured(self, request, queryset):
        queryset.update(is_featured=False)


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ("listing", "price", "changed_at", "note")
    readonly_fields = ("changed_at",)
    raw_id_fields = ("listing",)


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "notify_frequency", "is_active", "created_at")
    list_filter = ("is_active", "notify_frequency")
    search_fields = ("user__email", "name")
    readonly_fields = ("created_at", "updated_at", "last_notified_at")
