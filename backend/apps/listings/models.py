"""
Listing models: Listing, PriceHistory, and SavedSearch.
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Listing(models.Model):
    """
    A marketplace listing that wraps a Vehicle with pricing and status.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        PENDING = "pending", "Pending Review"
        SOLD = "sold", "Sold"
        EXPIRED = "expired", "Expired"
        REMOVED = "removed", "Removed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(
        "vehicles.Vehicle", on_delete=models.CASCADE, related_name="listings"
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="listings"
    )

    # Pricing
    price = models.DecimalField(max_digits=12, decimal_places=2)
    is_negotiable = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    # Status
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    # Location (may differ from dealer address for private sellers)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)

    # Engagement
    views_count = models.PositiveIntegerField(default=0)
    saves_count = models.PositiveIntegerField(default=0)
    inquiries_count = models.PositiveIntegerField(default=0)

    # Dates
    published_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    sold_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "-published_at"]
        verbose_name = "listing"
        verbose_name_plural = "listings"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["price"]),
            models.Index(fields=["-published_at"]),
            models.Index(fields=["zip_code"]),
        ]

    def __str__(self):
        return f"{self.vehicle} - ${self.price:,.2f}"

    def publish(self):
        """Move listing to active status."""
        self.status = self.Status.ACTIVE
        self.published_at = timezone.now()
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=60)
        self.save(update_fields=["status", "published_at", "expires_at", "updated_at"])

    def mark_sold(self):
        """Mark listing as sold."""
        self.status = self.Status.SOLD
        self.sold_at = timezone.now()
        self.save(update_fields=["status", "sold_at", "updated_at"])

    def increment_views(self):
        """Increment the view counter atomically."""
        Listing.objects.filter(pk=self.pk).update(views_count=models.F("views_count") + 1)


class PriceHistory(models.Model):
    """Tracks price changes for a listing over time."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="price_history"
    )
    price = models.DecimalField(max_digits=12, decimal_places=2)
    changed_at = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-changed_at"]
        verbose_name = "price history"
        verbose_name_plural = "price histories"

    def __str__(self):
        return f"{self.listing} -> ${self.price:,.2f} on {self.changed_at}"


class SavedSearch(models.Model):
    """A search configuration saved by a user for notification purposes."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_searches"
    )
    name = models.CharField(max_length=255)

    # Search parameters stored as JSON
    filters = models.JSONField(
        default=dict,
        help_text="Stored filter parameters, e.g. {make: 'Toyota', year_min: 2020, price_max: 30000}",
    )

    notify_email = models.BooleanField(default=True)
    notify_frequency = models.CharField(
        max_length=20,
        choices=[
            ("instant", "Instant"),
            ("daily", "Daily"),
            ("weekly", "Weekly"),
        ],
        default="daily",
    )

    last_notified_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "saved search"
        verbose_name_plural = "saved searches"

    def __str__(self):
        return f"{self.user.email}: {self.name}"
