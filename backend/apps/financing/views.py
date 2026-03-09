"""
Views for the financing app.
"""

from decimal import Decimal

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FinancingCalculation, LoanApplication
from .serializers import (
    FinancingCalculationInputSerializer,
    FinancingCalculationResultSerializer,
    FinancingCalculationSerializer,
    LoanApplicationCreateSerializer,
    LoanApplicationSerializer,
)
from .services import calculate_monthly_payment


class FinancingCalculateView(APIView):
    """
    Calculate monthly payment for a vehicle loan.

    Accepts vehicle price, down payment, trade-in value, interest rate,
    and loan term. Returns the computed monthly payment, total interest,
    total cost, and optionally a full amortization schedule.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = FinancingCalculationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        result = calculate_monthly_payment(
            vehicle_price=data["vehicle_price"],
            down_payment=data.get("down_payment", Decimal("0")),
            trade_in_value=data.get("trade_in_value", Decimal("0")),
            annual_interest_rate=data.get("annual_interest_rate", Decimal("5.0")),
            loan_term_months=data.get("loan_term_months", 60),
            sales_tax_rate=data.get("sales_tax_rate", Decimal("0")),
        )

        response_data = {
            "vehicle_price": data["vehicle_price"],
            "down_payment": data.get("down_payment", Decimal("0")),
            "trade_in_value": data.get("trade_in_value", Decimal("0")),
            "annual_interest_rate": data.get("annual_interest_rate", Decimal("5.0")),
            "loan_term_months": data.get("loan_term_months", 60),
            "sales_tax_rate": data.get("sales_tax_rate", Decimal("0")),
            "loan_amount": result.loan_amount,
            "monthly_payment": result.monthly_payment,
            "total_interest": result.total_interest,
            "total_cost": result.total_cost,
        }

        if data.get("include_schedule", False):
            response_data["amortization_schedule"] = result.amortization_schedule

        # Save calculation if user is authenticated
        if request.user.is_authenticated:
            listing_id = data.get("listing_id")
            FinancingCalculation.objects.create(
                user=request.user,
                listing_id=listing_id,
                vehicle_price=data["vehicle_price"],
                down_payment=data.get("down_payment", Decimal("0")),
                trade_in_value=data.get("trade_in_value", Decimal("0")),
                annual_interest_rate=data.get("annual_interest_rate", Decimal("5.0")),
                loan_term_months=data.get("loan_term_months", 60),
                sales_tax_rate=data.get("sales_tax_rate", Decimal("0")),
                loan_amount=result.loan_amount,
                monthly_payment=result.monthly_payment,
                total_interest=result.total_interest,
                total_cost=result.total_cost,
            )

        output_serializer = FinancingCalculationResultSerializer(response_data)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class MyCalculationsView(generics.ListAPIView):
    """List the authenticated user's financing calculations."""

    serializer_class = FinancingCalculationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FinancingCalculation.objects.filter(user=self.request.user)


class LoanApplicationCreateView(generics.CreateAPIView):
    """Submit a loan application."""

    serializer_class = LoanApplicationCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class LoanApplicationListView(generics.ListAPIView):
    """List the authenticated user's loan applications."""

    serializer_class = LoanApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LoanApplication.objects.filter(user=self.request.user)


class LoanApplicationDetailView(generics.RetrieveAPIView):
    """View details of a loan application."""

    serializer_class = LoanApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LoanApplication.objects.filter(user=self.request.user)
