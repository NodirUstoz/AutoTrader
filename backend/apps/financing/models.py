"""
Financing models: FinancingCalculation and LoanApplication.
"""

import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class FinancingCalculation(models.Model):
    """
    Stores a financing calculation performed by a user.
    Useful for saving and revisiting estimates.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="financing_calculations",
        null=True,
        blank=True,
    )
    listing = models.ForeignKey(
        "listings.Listing",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="financing_calculations",
    )

    # Inputs
    vehicle_price = models.DecimalField(max_digits=12, decimal_places=2)
    down_payment = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    trade_in_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    annual_interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(30)],
    )
    loan_term_months = models.PositiveIntegerField(
        validators=[MinValueValidator(6), MaxValueValidator(96)],
        help_text="Loan duration in months",
    )
    sales_tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )

    # Calculated outputs
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2)
    total_interest = models.DecimalField(max_digits=12, decimal_places=2)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "financing calculation"
        verbose_name_plural = "financing calculations"

    def __str__(self):
        return f"${self.monthly_payment}/mo for {self.loan_term_months} months"


class LoanApplication(models.Model):
    """
    Pre-qualification or full loan application submitted by a buyer.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        UNDER_REVIEW = "under_review", "Under Review"
        APPROVED = "approved", "Approved"
        DENIED = "denied", "Denied"
        WITHDRAWN = "withdrawn", "Withdrawn"

    class EmploymentStatus(models.TextChoices):
        EMPLOYED = "employed", "Employed"
        SELF_EMPLOYED = "self_employed", "Self-Employed"
        RETIRED = "retired", "Retired"
        STUDENT = "student", "Student"
        UNEMPLOYED = "unemployed", "Unemployed"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="loan_applications",
    )
    listing = models.ForeignKey(
        "listings.Listing",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="loan_applications",
    )
    calculation = models.ForeignKey(
        FinancingCalculation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="applications",
    )

    # Loan details
    requested_amount = models.DecimalField(max_digits=12, decimal_places=2)
    requested_term_months = models.PositiveIntegerField()
    down_payment = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Applicant information
    date_of_birth = models.DateField()
    ssn_last_four = models.CharField(max_length=4, help_text="Last 4 digits of SSN")
    employment_status = models.CharField(
        max_length=20,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.EMPLOYED,
    )
    employer_name = models.CharField(max_length=255, blank=True)
    annual_income = models.DecimalField(max_digits=12, decimal_places=2)
    monthly_housing_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Address
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)

    # Status tracking
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    decision_notes = models.TextField(blank=True)
    approved_rate = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    approved_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "loan application"
        verbose_name_plural = "loan applications"

    def __str__(self):
        return f"Loan application #{str(self.id)[:8]} - {self.user.email} - {self.get_status_display()}"
