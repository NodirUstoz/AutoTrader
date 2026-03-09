"""
Admin configuration for the accounts app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import BuyerProfile, DealerProfile, User


class DealerProfileInline(admin.StackedInline):
    model = DealerProfile
    can_delete = False
    verbose_name = "Dealer Profile"
    verbose_name_plural = "Dealer Profile"
    fk_name = "user"
    extra = 0


class BuyerProfileInline(admin.StackedInline):
    model = BuyerProfile
    can_delete = False
    verbose_name = "Buyer Profile"
    verbose_name_plural = "Buyer Profile"
    fk_name = "user"
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "is_verified",
        "date_joined",
    )
    list_filter = ("role", "is_active", "is_verified", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-date_joined",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "phone", "avatar")}),
        ("Role", {"fields": ("role",)}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_verified",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "role",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    def get_inlines(self, request, obj=None):
        if obj is None:
            return []
        if obj.role == User.Role.DEALER:
            return [DealerProfileInline]
        if obj.role == User.Role.BUYER:
            return [BuyerProfileInline]
        return []


@admin.register(DealerProfile)
class DealerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "business_name",
        "user",
        "city",
        "state",
        "is_verified",
        "rating",
        "created_at",
    )
    list_filter = ("is_verified", "state", "country")
    search_fields = ("business_name", "user__email", "city")
    readonly_fields = ("created_at", "updated_at")


@admin.register(BuyerProfile)
class BuyerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "zip_code", "search_radius_miles", "receive_notifications")
    search_fields = ("user__email",)
    readonly_fields = ("created_at", "updated_at")
