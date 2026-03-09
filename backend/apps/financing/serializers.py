"""
Serializers for the financing app.
"""

from decimal import Decimal

from rest_framework import serializers

from .models import FinancingCalculation, LoanApplication
from .services import calculate_monthly_payment


class FinancingCalculationInputSerializer(serializers.Serializer):
    """Input serializer for the financing calculator endpoint."""

    vehicle_price = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("1"))
    down_payment = serializers.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"), min_value=Decimal("0")
    )
    trade_in_value = serializers.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"), min_value=Decimal("0")
    )
    annual_interest_rate = serializers.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("5.0"), min_value=Decimal("0"), max_value=Decimal("30")
    )
    loan_term_months = serializers.IntegerField(default=60, min_value=6, max_value=96)
    sales_tax_rate = serializers.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0"), min_value=Decimal("0"), max_value=Decimal("20")
    )
    listing_id = serializers.UUIDField(required=False, allow_null=True)
    include_schedule = serializers.BooleanField(default=False)

    def validate(self, attrs):
        total_credits = attrs.get("down_payment", Decimal("0")) + attrs.get("trade_in_value", Decimal("0"))
        if total_credits >= attrs["vehicle_price"]:
            raise serializers.ValidationError(
                "Down payment plus trade-in value must be less than the vehicle price."
            )
        return attrs


class FinancingCalculationResultSerializer(serializers.Serializer):
    """Output serializer for financing calculation results."""

    vehicle_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    down_payment = serializers.DecimalField(max_digits=12, decimal_places=2)
    trade_in_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    annual_interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    loan_term_months = serializers.IntegerField()
    sales_tax_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    monthly_payment = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_interest = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_cost = serializers.DecimalField(max_digits=12, decimal_places=2)
    amortization_schedule = serializers.ListField(required=False)


class FinancingCalculationSerializer(serializers.ModelSerializer):
    """Read serializer for saved financing calculations."""

    class Meta:
        model = FinancingCalculation
        fields = (
            "id",
            "listing",
            "vehicle_price",
            "down_payment",
            "trade_in_value",
            "annual_interest_rate",
            "loan_term_months",
            "sales_tax_rate",
            "loan_amount",
            "monthly_payment",
            "total_interest",
            "total_cost",
            "created_at",
        )
        read_only_fields = ("id", "loan_amount", "monthly_payment", "total_interest", "total_cost", "created_at")


class LoanApplicationCreateSerializer(serializers.ModelSerializer):
    """Create a loan application."""

    class Meta:
        model = LoanApplication
        fields = (
            "listing",
            "calculation",
            "requested_amount",
            "requested_term_months",
            "down_payment",
            "date_of_birth",
            "ssn_last_four",
            "employment_status",
            "employer_name",
            "annual_income",
            "monthly_housing_payment",
            "address_line_1",
            "address_line_2",
            "city",
            "state",
            "zip_code",
        )

    def validate_ssn_last_four(self, value):
        if not value.isdigit() or len(value) != 4:
            raise serializers.ValidationError("Must be exactly 4 digits.")
        return value

    def validate_requested_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Requested amount must be positive.")
        return value

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        validated_data["status"] = LoanApplication.Status.SUBMITTED
        return super().create(validated_data)


class LoanApplicationSerializer(serializers.ModelSerializer):
    """Read serializer for loan applications."""

    status_display = serializers.CharField(source="get_status_display", read_only=True)
    employment_display = serializers.CharField(
        source="get_employment_status_display", read_only=True
    )

    class Meta:
        model = LoanApplication
        fields = (
            "id",
            "listing",
            "calculation",
            "requested_amount",
            "requested_term_months",
            "down_payment",
            "date_of_birth",
            "ssn_last_four",
            "employment_status",
            "employment_display",
            "employer_name",
            "annual_income",
            "monthly_housing_payment",
            "address_line_1",
            "address_line_2",
            "city",
            "state",
            "zip_code",
            "status",
            "status_display",
            "decision_notes",
            "approved_rate",
            "approved_amount",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "status",
            "decision_notes",
            "approved_rate",
            "approved_amount",
            "created_at",
            "updated_at",
        )
