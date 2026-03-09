"""
Financing calculation service.

Provides pure functions for loan payment mathematics, decoupled from
Django models so they can be used in serializers, views, or tasks.
"""

from decimal import ROUND_HALF_UP, Decimal
from typing import NamedTuple


class FinancingResult(NamedTuple):
    """Result of a financing calculation."""

    loan_amount: Decimal
    monthly_payment: Decimal
    total_interest: Decimal
    total_cost: Decimal
    amortization_schedule: list


def calculate_monthly_payment(
    vehicle_price: Decimal,
    down_payment: Decimal = Decimal("0"),
    trade_in_value: Decimal = Decimal("0"),
    annual_interest_rate: Decimal = Decimal("5.0"),
    loan_term_months: int = 60,
    sales_tax_rate: Decimal = Decimal("0"),
) -> FinancingResult:
    """
    Calculate the monthly payment for a vehicle loan.

    Uses the standard amortization formula:
        M = P * [r(1+r)^n] / [(1+r)^n - 1]

    where:
        M = monthly payment
        P = principal (loan amount)
        r = monthly interest rate
        n = number of payments
    """
    # Calculate taxable amount and loan principal
    taxable_amount = vehicle_price - trade_in_value
    sales_tax = (taxable_amount * sales_tax_rate / Decimal("100")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    loan_amount = (vehicle_price + sales_tax - down_payment - trade_in_value).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    if loan_amount <= 0:
        return FinancingResult(
            loan_amount=Decimal("0"),
            monthly_payment=Decimal("0"),
            total_interest=Decimal("0"),
            total_cost=vehicle_price + sales_tax,
            amortization_schedule=[],
        )

    # Monthly interest rate
    monthly_rate = annual_interest_rate / Decimal("1200")

    if monthly_rate == 0:
        # Zero-interest loan
        monthly_payment = (loan_amount / loan_term_months).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        total_cost = loan_amount + down_payment + trade_in_value
        schedule = _build_schedule_zero_interest(loan_amount, monthly_payment, loan_term_months)
        return FinancingResult(
            loan_amount=loan_amount,
            monthly_payment=monthly_payment,
            total_interest=Decimal("0"),
            total_cost=total_cost,
            amortization_schedule=schedule,
        )

    # Standard amortization formula
    rate_factor = (1 + monthly_rate) ** loan_term_months
    monthly_payment = (loan_amount * monthly_rate * rate_factor / (rate_factor - 1)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    total_paid = (monthly_payment * loan_term_months).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    total_interest = (total_paid - loan_amount).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    total_cost = (total_paid + down_payment + trade_in_value).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    schedule = _build_amortization_schedule(
        loan_amount, monthly_rate, monthly_payment, loan_term_months
    )

    return FinancingResult(
        loan_amount=loan_amount,
        monthly_payment=monthly_payment,
        total_interest=total_interest,
        total_cost=total_cost,
        amortization_schedule=schedule,
    )


def _build_amortization_schedule(
    principal: Decimal,
    monthly_rate: Decimal,
    monthly_payment: Decimal,
    term_months: int,
) -> list:
    """Build a month-by-month amortization schedule."""
    schedule = []
    balance = principal

    for month in range(1, term_months + 1):
        interest_payment = (balance * monthly_rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        principal_payment = monthly_payment - interest_payment

        # Adjust final payment
        if month == term_months:
            principal_payment = balance
            monthly_payment_actual = principal_payment + interest_payment
        else:
            monthly_payment_actual = monthly_payment

        balance = (balance - principal_payment).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if balance < 0:
            balance = Decimal("0")

        schedule.append(
            {
                "month": month,
                "payment": str(monthly_payment_actual),
                "principal": str(principal_payment),
                "interest": str(interest_payment),
                "balance": str(balance),
            }
        )

    return schedule


def _build_schedule_zero_interest(
    principal: Decimal, monthly_payment: Decimal, term_months: int
) -> list:
    """Build schedule for zero-interest loans."""
    schedule = []
    balance = principal

    for month in range(1, term_months + 1):
        payment = min(monthly_payment, balance)
        balance = (balance - payment).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if balance < 0:
            balance = Decimal("0")

        schedule.append(
            {
                "month": month,
                "payment": str(payment),
                "principal": str(payment),
                "interest": "0.00",
                "balance": str(balance),
            }
        )

    return schedule


def estimate_credit_score_rate(credit_score: int) -> Decimal:
    """
    Estimate an interest rate based on credit score tier.

    These are approximate averages and should not be used for real
    lending decisions.
    """
    if credit_score >= 780:
        return Decimal("3.5")
    elif credit_score >= 740:
        return Decimal("4.5")
    elif credit_score >= 700:
        return Decimal("5.5")
    elif credit_score >= 660:
        return Decimal("7.5")
    elif credit_score >= 620:
        return Decimal("10.0")
    elif credit_score >= 580:
        return Decimal("13.0")
    else:
        return Decimal("16.0")
