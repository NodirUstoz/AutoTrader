"""
Django-filter classes for the vehicles app.
"""

import django_filters

from .models import Vehicle


class VehicleFilter(django_filters.FilterSet):
    """
    Advanced filter for vehicle search.

    Supports range filters for year, mileage, and price (via listing),
    as well as exact/multiple-choice filters for categorical attributes.
    """

    # Year range
    year_min = django_filters.NumberFilter(field_name="year", lookup_expr="gte")
    year_max = django_filters.NumberFilter(field_name="year", lookup_expr="lte")

    # Mileage range
    mileage_min = django_filters.NumberFilter(field_name="mileage", lookup_expr="gte")
    mileage_max = django_filters.NumberFilter(field_name="mileage", lookup_expr="lte")

    # Price range (through listing)
    price_min = django_filters.NumberFilter(
        field_name="listings__price", lookup_expr="gte"
    )
    price_max = django_filters.NumberFilter(
        field_name="listings__price", lookup_expr="lte"
    )

    # Exact / icontains
    make = django_filters.UUIDFilter(field_name="make__id")
    make_name = django_filters.CharFilter(field_name="make__name", lookup_expr="iexact")
    model = django_filters.UUIDFilter(field_name="model__id")
    model_name = django_filters.CharFilter(field_name="model__name", lookup_expr="icontains")

    # Multiple choice
    fuel_type = django_filters.MultipleChoiceFilter(choices=Vehicle.FuelType.choices)
    transmission = django_filters.MultipleChoiceFilter(choices=Vehicle.Transmission.choices)
    drivetrain = django_filters.MultipleChoiceFilter(choices=Vehicle.Drivetrain.choices)
    body_type = django_filters.MultipleChoiceFilter(choices=Vehicle.BodyType.choices)
    condition = django_filters.MultipleChoiceFilter(choices=Vehicle.Condition.choices)
    vehicle_type = django_filters.MultipleChoiceFilter(choices=Vehicle.VehicleType.choices)

    # Color
    exterior_color = django_filters.CharFilter(lookup_expr="icontains")
    interior_color = django_filters.CharFilter(lookup_expr="icontains")

    # Features
    features = django_filters.UUIDFilter(field_name="features__id")

    # Text search
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Vehicle
        fields = [
            "year_min",
            "year_max",
            "mileage_min",
            "mileage_max",
            "price_min",
            "price_max",
            "make",
            "make_name",
            "model",
            "model_name",
            "fuel_type",
            "transmission",
            "drivetrain",
            "body_type",
            "condition",
            "vehicle_type",
            "exterior_color",
            "interior_color",
            "features",
        ]

    def filter_search(self, queryset, name, value):
        """Full-text-style search across make, model, trim, and description."""
        return queryset.filter(
            models.Q(make__name__icontains=value)
            | models.Q(model__name__icontains=value)
            | models.Q(trim__icontains=value)
            | models.Q(description__icontains=value)
        )

    @staticmethod
    def filter_search(queryset, name, value):
        from django.db.models import Q

        return queryset.filter(
            Q(make__name__icontains=value)
            | Q(model__name__icontains=value)
            | Q(trim__icontains=value)
            | Q(description__icontains=value)
        )
