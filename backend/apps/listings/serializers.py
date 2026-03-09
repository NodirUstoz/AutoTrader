"""
Serializers for the listings app.
"""

from rest_framework import serializers

from apps.vehicles.serializers import VehicleListSerializer

from .models import Listing, PriceHistory, SavedSearch


class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = ("id", "price", "changed_at", "note")
        read_only_fields = ("id", "changed_at")


class ListingListSerializer(serializers.ModelSerializer):
    """Lightweight listing serializer for list views."""

    vehicle = VehicleListSerializer(read_only=True)
    seller_name = serializers.CharField(source="seller.full_name", read_only=True)
    days_on_market = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = (
            "id",
            "vehicle",
            "price",
            "is_negotiable",
            "is_featured",
            "status",
            "city",
            "state",
            "zip_code",
            "views_count",
            "saves_count",
            "seller_name",
            "days_on_market",
            "published_at",
            "created_at",
        )

    def get_days_on_market(self, obj):
        if obj.published_at:
            from django.utils import timezone

            delta = timezone.now() - obj.published_at
            return delta.days
        return None


class ListingDetailSerializer(serializers.ModelSerializer):
    """Full listing serializer with price history."""

    vehicle = VehicleListSerializer(read_only=True)
    seller_name = serializers.CharField(source="seller.full_name", read_only=True)
    seller_id = serializers.UUIDField(source="seller.id", read_only=True)
    price_history = PriceHistorySerializer(many=True, read_only=True)
    days_on_market = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = (
            "id",
            "vehicle",
            "price",
            "is_negotiable",
            "is_featured",
            "status",
            "city",
            "state",
            "zip_code",
            "views_count",
            "saves_count",
            "inquiries_count",
            "seller_name",
            "seller_id",
            "days_on_market",
            "price_history",
            "published_at",
            "expires_at",
            "sold_at",
            "created_at",
            "updated_at",
        )

    def get_days_on_market(self, obj):
        if obj.published_at:
            from django.utils import timezone

            delta = timezone.now() - obj.published_at
            return delta.days
        return None


class ListingCreateSerializer(serializers.ModelSerializer):
    """Create or update a listing."""

    class Meta:
        model = Listing
        fields = (
            "vehicle",
            "price",
            "is_negotiable",
            "status",
            "city",
            "state",
            "zip_code",
        )

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate_vehicle(self, value):
        request = self.context.get("request")
        if request and value.seller != request.user:
            raise serializers.ValidationError("You can only create listings for your own vehicles.")
        return value

    def create(self, validated_data):
        validated_data["seller"] = self.context["request"].user
        listing = Listing.objects.create(**validated_data)

        # Record initial price in history
        PriceHistory.objects.create(
            listing=listing,
            price=listing.price,
            note="Initial listing price",
        )

        return listing

    def update(self, instance, validated_data):
        new_price = validated_data.get("price")
        if new_price and new_price != instance.price:
            PriceHistory.objects.create(
                listing=instance,
                price=new_price,
                note="Price updated",
            )
        return super().update(instance, validated_data)


class SavedSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedSearch
        fields = (
            "id",
            "name",
            "filters",
            "notify_email",
            "notify_frequency",
            "is_active",
            "last_notified_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "last_notified_at", "created_at", "updated_at")

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
