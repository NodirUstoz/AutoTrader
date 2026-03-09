"""
Vehicle catalog models.

Provides the core data model for vehicles, including make/model hierarchy,
images, and feature tagging.
"""

import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class VehicleMake(models.Model):
    """Manufacturer / brand (e.g. Toyota, Ford, BMW)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=100, blank=True)
    logo = models.ImageField(upload_to="makes/logos/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "vehicle make"
        verbose_name_plural = "vehicle makes"

    def __str__(self):
        return self.name


class VehicleModel(models.Model):
    """Specific model within a make (e.g. Camry, F-150, 3 Series)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    make = models.ForeignKey(VehicleMake, on_delete=models.CASCADE, related_name="models")
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["make__name", "name"]
        unique_together = ("make", "name")
        verbose_name = "vehicle model"
        verbose_name_plural = "vehicle models"

    def __str__(self):
        return f"{self.make.name} {self.name}"


class VehicleFeature(models.Model):
    """Selectable feature / option (e.g. Sunroof, Leather Seats)."""

    class Category(models.TextChoices):
        SAFETY = "safety", "Safety"
        COMFORT = "comfort", "Comfort"
        TECHNOLOGY = "technology", "Technology"
        PERFORMANCE = "performance", "Performance"
        EXTERIOR = "exterior", "Exterior"
        INTERIOR = "interior", "Interior"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, unique=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)

    class Meta:
        ordering = ["category", "name"]
        verbose_name = "vehicle feature"
        verbose_name_plural = "vehicle features"

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    """
    Central vehicle record.

    Represents a specific physical vehicle with its characteristics.
    Linked to a seller (user) and may have many images and features.
    """

    class VehicleType(models.TextChoices):
        CAR = "car", "Car"
        TRUCK = "truck", "Truck"
        SUV = "suv", "SUV"
        VAN = "van", "Van"
        MOTORCYCLE = "motorcycle", "Motorcycle"
        RV = "rv", "RV"
        OTHER = "other", "Other"

    class FuelType(models.TextChoices):
        GASOLINE = "gasoline", "Gasoline"
        DIESEL = "diesel", "Diesel"
        ELECTRIC = "electric", "Electric"
        HYBRID = "hybrid", "Hybrid"
        PLUGIN_HYBRID = "plugin_hybrid", "Plug-in Hybrid"
        HYDROGEN = "hydrogen", "Hydrogen"
        OTHER = "other", "Other"

    class Transmission(models.TextChoices):
        AUTOMATIC = "automatic", "Automatic"
        MANUAL = "manual", "Manual"
        CVT = "cvt", "CVT"
        DUAL_CLUTCH = "dual_clutch", "Dual Clutch"
        OTHER = "other", "Other"

    class Drivetrain(models.TextChoices):
        FWD = "fwd", "Front-Wheel Drive"
        RWD = "rwd", "Rear-Wheel Drive"
        AWD = "awd", "All-Wheel Drive"
        FOUR_WD = "4wd", "Four-Wheel Drive"

    class Condition(models.TextChoices):
        NEW = "new", "New"
        USED = "used", "Used"
        CERTIFIED = "certified", "Certified Pre-Owned"

    class BodyType(models.TextChoices):
        SEDAN = "sedan", "Sedan"
        COUPE = "coupe", "Coupe"
        CONVERTIBLE = "convertible", "Convertible"
        HATCHBACK = "hatchback", "Hatchback"
        WAGON = "wagon", "Wagon"
        SUV = "suv", "SUV"
        CROSSOVER = "crossover", "Crossover"
        PICKUP = "pickup", "Pickup Truck"
        MINIVAN = "minivan", "Minivan"
        VAN = "van", "Van"
        MOTORCYCLE = "motorcycle", "Motorcycle"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vehicles"
    )

    # Core attributes
    vin = models.CharField(max_length=17, unique=True, blank=True, null=True, verbose_name="VIN")
    make = models.ForeignKey(VehicleMake, on_delete=models.PROTECT, related_name="vehicles")
    model = models.ForeignKey(VehicleModel, on_delete=models.PROTECT, related_name="vehicles")
    year = models.PositiveIntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )
    trim = models.CharField(max_length=100, blank=True)
    vehicle_type = models.CharField(max_length=20, choices=VehicleType.choices, default=VehicleType.CAR)
    body_type = models.CharField(max_length=20, choices=BodyType.choices, default=BodyType.SEDAN)

    # Mechanical
    fuel_type = models.CharField(max_length=20, choices=FuelType.choices, default=FuelType.GASOLINE)
    transmission = models.CharField(max_length=20, choices=Transmission.choices, default=Transmission.AUTOMATIC)
    drivetrain = models.CharField(max_length=10, choices=Drivetrain.choices, default=Drivetrain.FWD)
    engine = models.CharField(max_length=100, blank=True, help_text="e.g. 2.5L 4-Cylinder")
    horsepower = models.PositiveIntegerField(null=True, blank=True)
    cylinders = models.PositiveIntegerField(null=True, blank=True)

    # Condition
    condition = models.CharField(max_length=20, choices=Condition.choices, default=Condition.USED)
    mileage = models.PositiveIntegerField(default=0, help_text="Odometer reading in miles")

    # Appearance
    exterior_color = models.CharField(max_length=50, blank=True)
    interior_color = models.CharField(max_length=50, blank=True)

    # Efficiency
    mpg_city = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    mpg_highway = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)

    # Capacity
    doors = models.PositiveIntegerField(default=4)
    seats = models.PositiveIntegerField(default=5)

    # Description
    description = models.TextField(blank=True)

    # Features (many-to-many)
    features = models.ManyToManyField(VehicleFeature, blank=True, related_name="vehicles")

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "vehicle"
        verbose_name_plural = "vehicles"
        indexes = [
            models.Index(fields=["year"]),
            models.Index(fields=["mileage"]),
            models.Index(fields=["fuel_type"]),
            models.Index(fields=["transmission"]),
            models.Index(fields=["condition"]),
            models.Index(fields=["body_type"]),
            models.Index(fields=["vin"]),
        ]

    def __str__(self):
        return f"{self.year} {self.make.name} {self.model.name}"

    @property
    def title(self):
        parts = [str(self.year), self.make.name, self.model.name]
        if self.trim:
            parts.append(self.trim)
        return " ".join(parts)

    @property
    def mpg_combined(self):
        if self.mpg_city and self.mpg_highway:
            return round((self.mpg_city + self.mpg_highway) / 2, 1)
        return None


class VehicleImage(models.Model):
    """Image associated with a vehicle."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="vehicles/%Y/%m/")
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-is_primary"]
        verbose_name = "vehicle image"
        verbose_name_plural = "vehicle images"

    def __str__(self):
        return f"Image for {self.vehicle} (order={self.order})"

    def save(self, *args, **kwargs):
        # Ensure only one primary image per vehicle
        if self.is_primary:
            VehicleImage.objects.filter(vehicle=self.vehicle, is_primary=True).exclude(
                pk=self.pk
            ).update(is_primary=False)
        super().save(*args, **kwargs)
