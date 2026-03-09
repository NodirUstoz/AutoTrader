"""
Serializers for the comparisons app.
"""

from rest_framework import serializers

from apps.vehicles.models import Vehicle
from apps.vehicles.serializers import VehicleDetailSerializer

from .models import VehicleComparison


class VehicleComparisonCreateSerializer(serializers.ModelSerializer):
    """Create or update a comparison."""

    vehicle_ids = serializers.PrimaryKeyRelatedField(
        queryset=Vehicle.objects.all(),
        many=True,
        write_only=True,
    )

    class Meta:
        model = VehicleComparison
        fields = ("title", "vehicle_ids")

    def validate_vehicle_ids(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Select at least 2 vehicles to compare.")
        if len(value) > 4:
            raise serializers.ValidationError("You can compare at most 4 vehicles.")
        return value

    def create(self, validated_data):
        vehicles = validated_data.pop("vehicle_ids")
        request = self.context.get("request")

        comparison = VehicleComparison.objects.create(
            user=request.user if request and request.user.is_authenticated else None,
            title=validated_data.get("title", ""),
            session_key=request.session.session_key or "" if request else "",
        )
        comparison.vehicles.set(vehicles)
        return comparison

    def update(self, instance, validated_data):
        vehicles = validated_data.pop("vehicle_ids", None)
        if "title" in validated_data:
            instance.title = validated_data["title"]
            instance.save(update_fields=["title", "updated_at"])
        if vehicles is not None:
            instance.vehicles.set(vehicles)
        return instance


class VehicleComparisonSerializer(serializers.ModelSerializer):
    """Read serializer with full vehicle details."""

    vehicles = VehicleDetailSerializer(many=True, read_only=True)
    vehicle_count = serializers.SerializerMethodField()

    class Meta:
        model = VehicleComparison
        fields = (
            "id",
            "title",
            "vehicles",
            "vehicle_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_vehicle_count(self, obj):
        return obj.vehicles.count()
