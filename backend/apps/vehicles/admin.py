"""
Admin configuration for the vehicles app.
"""

from django.contrib import admin

from .models import Vehicle, VehicleFeature, VehicleImage, VehicleMake, VehicleModel


class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1
    fields = ("image", "alt_text", "is_primary", "order")


@admin.register(VehicleMake)
class VehicleMakeAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "is_active")
    list_filter = ("is_active", "country")
    search_fields = ("name",)


@admin.register(VehicleModel)
class VehicleModelAdmin(admin.ModelAdmin):
    list_display = ("name", "make", "is_active")
    list_filter = ("is_active", "make")
    search_fields = ("name", "make__name")


@admin.register(VehicleFeature)
class VehicleFeatureAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    list_filter = ("category",)
    search_fields = ("name",)


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "vin",
        "year",
        "vehicle_type",
        "condition",
        "mileage",
        "fuel_type",
        "seller",
        "created_at",
    )
    list_filter = (
        "vehicle_type",
        "condition",
        "fuel_type",
        "transmission",
        "body_type",
        "make",
    )
    search_fields = ("vin", "make__name", "model__name", "seller__email")
    readonly_fields = ("created_at", "updated_at")
    inlines = [VehicleImageInline]
    filter_horizontal = ("features",)
    raw_id_fields = ("seller", "make", "model")

    def title(self, obj):
        return obj.title

    title.short_description = "Vehicle"


@admin.register(VehicleImage)
class VehicleImageAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "is_primary", "order", "uploaded_at")
    list_filter = ("is_primary",)
    raw_id_fields = ("vehicle",)
