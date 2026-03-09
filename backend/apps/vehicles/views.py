"""
Views for the vehicles app.
"""

import logging

from django.db.models import Prefetch
from rest_framework import generics, parsers, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsDealerUser, IsOwnerOrReadOnly
from utils.vin_decoder import decode_vin

from .filters import VehicleFilter
from .models import Vehicle, VehicleFeature, VehicleImage, VehicleMake, VehicleModel
from .serializers import (
    VehicleCreateSerializer,
    VehicleDetailSerializer,
    VehicleFeatureSerializer,
    VehicleImageSerializer,
    VehicleImageUploadSerializer,
    VehicleListSerializer,
    VehicleMakeSerializer,
    VehicleModelSerializer,
)

logger = logging.getLogger(__name__)


class VehicleMakeListView(generics.ListAPIView):
    """List all active vehicle makes."""

    queryset = VehicleMake.objects.filter(is_active=True)
    serializer_class = VehicleMakeSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class VehicleModelListView(generics.ListAPIView):
    """List vehicle models, optionally filtered by make."""

    serializer_class = VehicleModelSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        queryset = VehicleModel.objects.select_related("make").filter(is_active=True)
        make_id = self.request.query_params.get("make")
        if make_id:
            queryset = queryset.filter(make_id=make_id)
        return queryset


class VehicleFeatureListView(generics.ListAPIView):
    """List all vehicle features grouped by category."""

    queryset = VehicleFeature.objects.all()
    serializer_class = VehicleFeatureSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class VehicleListView(generics.ListAPIView):
    """
    List vehicles with advanced filtering.

    Supports filtering by make, model, year range, price range, mileage,
    fuel type, transmission, body type, condition, and more.
    """

    serializer_class = VehicleListSerializer
    permission_classes = [permissions.AllowAny]
    filterset_class = VehicleFilter

    def get_queryset(self):
        return (
            Vehicle.objects.select_related("make", "model", "seller")
            .prefetch_related(
                Prefetch(
                    "images",
                    queryset=VehicleImage.objects.filter(is_primary=True),
                ),
                "listings",
            )
            .all()
        )


class VehicleCreateView(generics.CreateAPIView):
    """Create a new vehicle (dealers only)."""

    serializer_class = VehicleCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsDealerUser]


class VehicleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a vehicle."""

    queryset = Vehicle.objects.select_related("make", "model", "seller").prefetch_related(
        "images", "features"
    )
    permission_classes = [IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return VehicleCreateSerializer
        return VehicleDetailSerializer

    def perform_destroy(self, instance):
        logger.info(
            "Vehicle %s (%s) deleted by user %s",
            instance.id,
            instance.title,
            self.request.user.id,
        )
        instance.delete()


class VehicleImageUploadView(APIView):
    """Upload images for a vehicle."""

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request, vehicle_id):
        try:
            vehicle = Vehicle.objects.get(id=vehicle_id, seller=request.user)
        except Vehicle.DoesNotExist:
            return Response(
                {"detail": "Vehicle not found or you are not the owner."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = VehicleImageUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        images_data = serializer.validated_data["images"]
        primary_index = serializer.validated_data.get("is_primary_index", 0)
        existing_count = vehicle.images.count()

        created_images = []
        for idx, image_file in enumerate(images_data):
            order = existing_count + idx
            is_primary = idx == primary_index and existing_count == 0
            img = VehicleImage.objects.create(
                vehicle=vehicle,
                image=image_file,
                is_primary=is_primary,
                order=order,
            )
            created_images.append(img)

        return Response(
            VehicleImageSerializer(created_images, many=True).data,
            status=status.HTTP_201_CREATED,
        )


class VINDecodeView(APIView):
    """Decode a VIN using the NHTSA API."""

    permission_classes = [permissions.AllowAny]

    def get(self, request, vin):
        if len(vin) != 17:
            return Response(
                {"detail": "VIN must be exactly 17 characters."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = decode_vin(vin)
        if result is None:
            return Response(
                {"detail": "Unable to decode VIN. Please try again later."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(result, status=status.HTTP_200_OK)


class MyVehiclesView(generics.ListAPIView):
    """List vehicles owned by the authenticated user."""

    serializer_class = VehicleListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Vehicle.objects.filter(seller=self.request.user)
            .select_related("make", "model")
            .prefetch_related("images", "listings")
        )
