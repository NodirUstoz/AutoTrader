"""
Inquiry models: Inquiry and TestDriveRequest.
"""

import uuid

from django.conf import settings
from django.db import models


class Inquiry(models.Model):
    """
    A message sent by a buyer to a seller regarding a listing.
    """

    class Status(models.TextChoices):
        NEW = "new", "New"
        READ = "read", "Read"
        REPLIED = "replied", "Replied"
        CLOSED = "closed", "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(
        "listings.Listing", on_delete=models.CASCADE, related_name="inquiries"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_inquiries"
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_inquiries",
    )
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.NEW)

    # Contact preferences
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=[("email", "Email"), ("phone", "Phone"), ("either", "Either")],
        default="email",
    )
    phone_number = models.CharField(max_length=20, blank=True)

    # Reply (seller response)
    reply_message = models.TextField(blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "inquiry"
        verbose_name_plural = "inquiries"

    def __str__(self):
        return f"Inquiry from {self.sender.email} re: {self.listing}"


class TestDriveRequest(models.Model):
    """
    A request from a buyer to schedule a test drive.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No Show"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(
        "listings.Listing", on_delete=models.CASCADE, related_name="test_drives"
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="test_drive_requests",
    )
    dealer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="test_drive_appointments",
    )

    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    alternate_date = models.DateField(null=True, blank=True)
    alternate_time = models.TimeField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)

    # Contact info
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()

    # Confirmed details
    confirmed_date = models.DateField(null=True, blank=True)
    confirmed_time = models.TimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "test drive request"
        verbose_name_plural = "test drive requests"

    def __str__(self):
        return (
            f"Test drive: {self.requester.email} - "
            f"{self.listing.vehicle} on {self.preferred_date}"
        )
