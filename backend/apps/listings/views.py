"""
Views for the listings app.
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.accounts.permissions import IsOwnerOrReadOnly

from .models import Listing, SavedSearch
from .serializers import (
    ListingCreateSerializer,
    ListingDetailSerializer,
    ListingListSerializer,
    SavedSearchSerializer,
)


class ListingListView(generics.ListAPIView):
    """Browse active listings with filtering and ordering."""

    serializer_class = ListingListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "is_featured", "is_negotiable", "city", "state"]
    search_fields = [
        "vehicle__make__name",
        "vehicle__model__name",
        "vehicle__trim",
        "city",
        "state",
    ]
    ordering_fields = ["price", "published_at", "views_count", "vehicle__year", "vehicle__mileage"]
    ordering = ["-is_featured", "-published_at"]

    def get_queryset(self):
        queryset = (
            Listing.objects.select_related("vehicle__make", "vehicle__model", "seller")
            .prefetch_related("vehicle__images")
            .filter(status=Listing.Status.ACTIVE)
        )

        # Price range filters
        price_min = self.request.query_params.get("price_min")
        price_max = self.request.query_params.get("price_max")
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        if price_max:
            queryset = queryset.filter(price__lte=price_max)

        return queryset


class ListingCreateView(generics.CreateAPIView):
    """Create a new listing."""

    serializer_class = ListingCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class ListingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a listing."""

    queryset = Listing.objects.select_related(
        "vehicle__make", "vehicle__model", "seller"
    ).prefetch_related("vehicle__images", "price_history")
    permission_classes = [IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return ListingCreateSerializer
        return ListingDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increment_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class MyListingsView(generics.ListAPIView):
    """List the authenticated user's own listings."""

    serializer_class = ListingListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Listing.objects.filter(seller=self.request.user)
            .select_related("vehicle__make", "vehicle__model", "seller")
            .prefetch_related("vehicle__images")
        )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def publish_listing(request, pk):
    """Publish a draft listing to make it active."""
    try:
        listing = Listing.objects.get(pk=pk, seller=request.user)
    except Listing.DoesNotExist:
        return Response(
            {"detail": "Listing not found."}, status=status.HTTP_404_NOT_FOUND
        )

    if listing.status not in (Listing.Status.DRAFT, Listing.Status.PENDING):
        return Response(
            {"detail": f"Cannot publish a listing with status '{listing.status}'."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    listing.publish()
    return Response(
        ListingDetailSerializer(listing).data, status=status.HTTP_200_OK
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def mark_listing_sold(request, pk):
    """Mark a listing as sold."""
    try:
        listing = Listing.objects.get(pk=pk, seller=request.user)
    except Listing.DoesNotExist:
        return Response(
            {"detail": "Listing not found."}, status=status.HTTP_404_NOT_FOUND
        )

    if listing.status != Listing.Status.ACTIVE:
        return Response(
            {"detail": "Only active listings can be marked as sold."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    listing.mark_sold()
    return Response(
        ListingDetailSerializer(listing).data, status=status.HTTP_200_OK
    )


class SavedSearchListCreateView(generics.ListCreateAPIView):
    """List and create saved searches for the authenticated user."""

    serializer_class = SavedSearchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedSearch.objects.filter(user=self.request.user)


class SavedSearchDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Manage a single saved search."""

    serializer_class = SavedSearchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedSearch.objects.filter(user=self.request.user)
