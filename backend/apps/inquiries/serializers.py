"""
Serializers for the inquiries app.
"""

from rest_framework import serializers

from .models import Inquiry, TestDriveRequest


class InquiryCreateSerializer(serializers.ModelSerializer):
    """Create an inquiry to a seller about a listing."""

    class Meta:
        model = Inquiry
        fields = (
            "listing",
            "subject",
            "message",
            "preferred_contact_method",
            "phone_number",
        )

    def validate_listing(self, value):
        request = self.context.get("request")
        if request and value.seller == request.user:
            raise serializers.ValidationError("You cannot send an inquiry to yourself.")
        if value.status != "active":
            raise serializers.ValidationError("This listing is no longer active.")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["sender"] = request.user
        validated_data["recipient"] = validated_data["listing"].seller
        return super().create(validated_data)


class InquiryListSerializer(serializers.ModelSerializer):
    """List view for inquiries."""

    sender_name = serializers.CharField(source="sender.full_name", read_only=True)
    sender_email = serializers.EmailField(source="sender.email", read_only=True)
    listing_title = serializers.SerializerMethodField()

    class Meta:
        model = Inquiry
        fields = (
            "id",
            "listing",
            "sender_name",
            "sender_email",
            "subject",
            "status",
            "preferred_contact_method",
            "created_at",
            "listing_title",
        )

    def get_listing_title(self, obj):
        return str(obj.listing.vehicle)


class InquiryDetailSerializer(serializers.ModelSerializer):
    """Full detail for a single inquiry."""

    sender_name = serializers.CharField(source="sender.full_name", read_only=True)
    sender_email = serializers.EmailField(source="sender.email", read_only=True)
    recipient_name = serializers.CharField(source="recipient.full_name", read_only=True)
    listing_title = serializers.SerializerMethodField()

    class Meta:
        model = Inquiry
        fields = (
            "id",
            "listing",
            "sender_name",
            "sender_email",
            "recipient_name",
            "subject",
            "message",
            "status",
            "preferred_contact_method",
            "phone_number",
            "reply_message",
            "replied_at",
            "listing_title",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "listing",
            "sender_name",
            "sender_email",
            "recipient_name",
            "created_at",
            "updated_at",
        )

    def get_listing_title(self, obj):
        return str(obj.listing.vehicle)


class InquiryReplySerializer(serializers.Serializer):
    """Reply to an inquiry."""

    reply_message = serializers.CharField()


class TestDriveRequestCreateSerializer(serializers.ModelSerializer):
    """Create a test drive request."""

    class Meta:
        model = TestDriveRequest
        fields = (
            "listing",
            "preferred_date",
            "preferred_time",
            "alternate_date",
            "alternate_time",
            "notes",
            "contact_phone",
            "contact_email",
        )

    def validate_listing(self, value):
        if value.status != "active":
            raise serializers.ValidationError("This listing is no longer active.")
        return value

    def validate_preferred_date(self, value):
        from datetime import date

        if value < date.today():
            raise serializers.ValidationError("Preferred date cannot be in the past.")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["requester"] = request.user
        validated_data["dealer"] = validated_data["listing"].seller
        return super().create(validated_data)


class TestDriveRequestSerializer(serializers.ModelSerializer):
    """Full serializer for test drive requests."""

    requester_name = serializers.CharField(source="requester.full_name", read_only=True)
    listing_title = serializers.SerializerMethodField()

    class Meta:
        model = TestDriveRequest
        fields = (
            "id",
            "listing",
            "requester_name",
            "preferred_date",
            "preferred_time",
            "alternate_date",
            "alternate_time",
            "status",
            "notes",
            "contact_phone",
            "contact_email",
            "confirmed_date",
            "confirmed_time",
            "listing_title",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_listing_title(self, obj):
        return str(obj.listing.vehicle)
