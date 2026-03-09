"""
Serializers for the accounts app.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import BuyerProfile, DealerProfile

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Handles new user registration with password confirmation."""

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "phone",
            "role",
            "password",
            "password_confirm",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Create the appropriate profile
        if user.role == User.Role.DEALER:
            DealerProfile.objects.create(
                user=user,
                business_name=f"{user.full_name}'s Dealership",
                address_line_1="",
                city="",
                state="",
                zip_code="",
            )
        else:
            BuyerProfile.objects.create(user=user)

        return user


class UserSerializer(serializers.ModelSerializer):
    """Read serializer for user data."""

    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "role",
            "avatar",
            "is_verified",
            "date_joined",
        )
        read_only_fields = ("id", "email", "role", "is_verified", "date_joined")


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Handles updates to the user's own profile."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone", "avatar")


class ChangePasswordSerializer(serializers.Serializer):
    """Validates old and new password for password change."""

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "New passwords do not match."}
            )
        return attrs

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class DealerProfileSerializer(serializers.ModelSerializer):
    """Full dealer profile serializer."""

    user = UserSerializer(read_only=True)
    full_address = serializers.ReadOnlyField()

    class Meta:
        model = DealerProfile
        fields = (
            "id",
            "user",
            "business_name",
            "license_number",
            "website",
            "description",
            "logo",
            "banner",
            "address_line_1",
            "address_line_2",
            "city",
            "state",
            "zip_code",
            "country",
            "latitude",
            "longitude",
            "year_established",
            "is_verified",
            "rating",
            "total_reviews",
            "operating_hours",
            "full_address",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "is_verified", "rating", "total_reviews", "created_at", "updated_at")


class DealerProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for dealers to update their own profile."""

    class Meta:
        model = DealerProfile
        fields = (
            "business_name",
            "license_number",
            "website",
            "description",
            "logo",
            "banner",
            "address_line_1",
            "address_line_2",
            "city",
            "state",
            "zip_code",
            "country",
            "latitude",
            "longitude",
            "year_established",
            "operating_hours",
        )


class BuyerProfileSerializer(serializers.ModelSerializer):
    """Full buyer profile serializer."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = BuyerProfile
        fields = (
            "id",
            "user",
            "zip_code",
            "search_radius_miles",
            "preferred_makes",
            "preferred_body_types",
            "min_budget",
            "max_budget",
            "receive_notifications",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class DealerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for dealer listings."""

    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = DealerProfile
        fields = (
            "id",
            "user_name",
            "business_name",
            "city",
            "state",
            "is_verified",
            "rating",
            "total_reviews",
            "logo",
        )
