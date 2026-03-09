"""
Serializers for the vehicles app.
"""

from rest_framework import serializers

from .models import Vehicle, VehicleFeature, VehicleImage, VehicleMake, VehicleModel


class VehicleMakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleMake
        fields = ("id", "name", "country", "logo")


class VehicleModelSerializer(serializers.ModelSerializer):
    make_name = serializers.CharField(source="make.name", read_only=True)

    class Meta:
        model = VehicleModel
        fields = ("id", "make", "make_name", "name")


class VehicleFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleFeature
        fields = ("id", "name", "category")


class VehicleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImage
        fields = ("id", "image", "alt_text", "is_primary", "order", "uploaded_at")
        read_only_fields = ("id", "uploaded_at")


class VehicleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for vehicle lists and search results."""

    make_name = serializers.CharField(source="make.name", read_only=True)
    model_name = serializers.CharField(source="model.name", read_only=True)
    title = serializers.ReadOnlyField()
    primary_image = serializers.SerializerMethodField()
    listing_price = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = (
            "id",
            "title",
            "make_name",
            "model_name",
            "year",
            "trim",
            "vehicle_type",
            "body_type",
            "fuel_type",
            "transmission",
            "drivetrain",
            "condition",
            "mileage",
            "exterior_color",
            "primary_image",
            "listing_price",
            "created_at",
        )

    def get_primary_image(self, obj):
        image = obj.images.filter(is_primary=True).first()
        if not image:
            image = obj.images.first()
        if image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(image.image.url)
            return image.image.url
        return None

    def get_listing_price(self, obj):
        listing = obj.listings.filter(status="active").first()
        if listing:
            return str(listing.price)
        return None


class VehicleDetailSerializer(serializers.ModelSerializer):
    """Full serializer for vehicle detail view."""

    make = VehicleMakeSerializer(read_only=True)
    model = VehicleModelSerializer(read_only=True)
    features = VehicleFeatureSerializer(many=True, read_only=True)
    images = VehicleImageSerializer(many=True, read_only=True)
    title = serializers.ReadOnlyField()
    mpg_combined = serializers.ReadOnlyField()
    seller_name = serializers.CharField(source="seller.full_name", read_only=True)
    seller_id = serializers.UUIDField(source="seller.id", read_only=True)

    class Meta:
        model = Vehicle
        fields = (
            "id",
            "title",
            "vin",
            "make",
            "model",
            "year",
            "trim",
            "vehicle_type",
            "body_type",
            "fuel_type",
            "transmission",
            "drivetrain",
            "engine",
            "horsepower",
            "cylinders",
            "condition",
            "mileage",
            "exterior_color",
            "interior_color",
            "mpg_city",
            "mpg_highway",
            "mpg_combined",
            "doors",
            "seats",
            "description",
            "features",
            "images",
            "seller_name",
            "seller_id",
            "created_at",
            "updated_at",
        )


class VehicleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating vehicles."""

    feature_ids = serializers.PrimaryKeyRelatedField(
        queryset=VehicleFeature.objects.all(),
        many=True,
        required=False,
        write_only=True,
    )

    class Meta:
        model = Vehicle
        fields = (
            "vin",
            "make",
            "model",
            "year",
            "trim",
            "vehicle_type",
            "body_type",
            "fuel_type",
            "transmission",
            "drivetrain",
            "engine",
            "horsepower",
            "cylinders",
            "condition",
            "mileage",
            "exterior_color",
            "interior_color",
            "mpg_city",
            "mpg_highway",
            "doors",
            "seats",
            "description",
            "feature_ids",
        )

    def validate_year(self, value):
        import datetime

        current_year = datetime.date.today().year
        if value > current_year + 2:
            raise serializers.ValidationError(
                f"Year cannot be more than {current_year + 2}."
            )
        return value

    def validate_vin(self, value):
        if value and len(value) != 17:
            raise serializers.ValidationError("VIN must be exactly 17 characters.")
        return value

    def create(self, validated_data):
        features = validated_data.pop("feature_ids", [])
        validated_data["seller"] = self.context["request"].user
        vehicle = Vehicle.objects.create(**validated_data)
        if features:
            vehicle.features.set(features)
        return vehicle

    def update(self, instance, validated_data):
        features = validated_data.pop("feature_ids", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if features is not None:
            instance.features.set(features)
        return instance


class VehicleImageUploadSerializer(serializers.Serializer):
    """Handles bulk image upload for a vehicle."""

    images = serializers.ListField(
        child=serializers.ImageField(), max_length=20
    )
    is_primary_index = serializers.IntegerField(
        required=False,
        default=0,
        help_text="Index of the image in the list that should be set as primary.",
    )
