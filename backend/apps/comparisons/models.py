"""
Comparison model: allows users to compare up to four vehicles side by side.
"""

import uuid

from django.conf import settings
from django.db import models


class VehicleComparison(models.Model):
    """
    Stores a comparison session containing two to four vehicles.

    Anonymous comparisons are supported (user may be null).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comparisons",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255, blank=True)
    vehicles = models.ManyToManyField(
        "vehicles.Vehicle", related_name="comparisons", blank=True
    )
    session_key = models.CharField(
        max_length=64,
        blank=True,
        help_text="Session key for anonymous comparison tracking.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "vehicle comparison"
        verbose_name_plural = "vehicle comparisons"

    def __str__(self):
        vehicle_count = self.vehicles.count()
        owner = self.user.email if self.user else "anonymous"
        return f"Comparison ({vehicle_count} vehicles) by {owner}"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.pk and self.vehicles.count() > 4:
            raise ValidationError("A comparison can contain at most 4 vehicles.")
