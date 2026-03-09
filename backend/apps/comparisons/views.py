"""
Views for the comparisons app.
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import VehicleComparison
from .serializers import VehicleComparisonCreateSerializer, VehicleComparisonSerializer


class ComparisonCreateView(generics.CreateAPIView):
    """Create a new vehicle comparison."""

    serializer_class = VehicleComparisonCreateSerializer
    permission_classes = [permissions.AllowAny]


class ComparisonDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a comparison."""

    queryset = VehicleComparison.objects.prefetch_related(
        "vehicles__make",
        "vehicles__model",
        "vehicles__features",
        "vehicles__images",
    )
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return VehicleComparisonCreateSerializer
        return VehicleComparisonSerializer


class MyComparisonsView(generics.ListAPIView):
    """List comparisons for the authenticated user."""

    serializer_class = VehicleComparisonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return VehicleComparison.objects.filter(
            user=self.request.user
        ).prefetch_related("vehicles__make", "vehicles__model")


class ComparisonAddVehicleView(APIView):
    """Add a vehicle to an existing comparison."""

    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        try:
            comparison = VehicleComparison.objects.get(pk=pk)
        except VehicleComparison.DoesNotExist:
            return Response(
                {"detail": "Comparison not found."}, status=status.HTTP_404_NOT_FOUND
            )

        vehicle_id = request.data.get("vehicle_id")
        if not vehicle_id:
            return Response(
                {"detail": "vehicle_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if comparison.vehicles.count() >= 4:
            return Response(
                {"detail": "A comparison can contain at most 4 vehicles."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from apps.vehicles.models import Vehicle

        try:
            vehicle = Vehicle.objects.get(pk=vehicle_id)
        except Vehicle.DoesNotExist:
            return Response(
                {"detail": "Vehicle not found."}, status=status.HTTP_404_NOT_FOUND
            )

        comparison.vehicles.add(vehicle)
        return Response(
            VehicleComparisonSerializer(comparison).data, status=status.HTTP_200_OK
        )


class ComparisonRemoveVehicleView(APIView):
    """Remove a vehicle from an existing comparison."""

    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        try:
            comparison = VehicleComparison.objects.get(pk=pk)
        except VehicleComparison.DoesNotExist:
            return Response(
                {"detail": "Comparison not found."}, status=status.HTTP_404_NOT_FOUND
            )

        vehicle_id = request.data.get("vehicle_id")
        if not vehicle_id:
            return Response(
                {"detail": "vehicle_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        comparison.vehicles.remove(vehicle_id)
        return Response(
            VehicleComparisonSerializer(comparison).data, status=status.HTTP_200_OK
        )
