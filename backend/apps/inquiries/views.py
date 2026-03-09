"""
Views for the inquiries app.
"""

from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Inquiry, TestDriveRequest
from .serializers import (
    InquiryCreateSerializer,
    InquiryDetailSerializer,
    InquiryListSerializer,
    InquiryReplySerializer,
    TestDriveRequestCreateSerializer,
    TestDriveRequestSerializer,
)


class InquiryCreateView(generics.CreateAPIView):
    """Send an inquiry to a seller about a listing."""

    serializer_class = InquiryCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class InquirySentListView(generics.ListAPIView):
    """List inquiries sent by the authenticated user."""

    serializer_class = InquiryListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Inquiry.objects.filter(sender=self.request.user).select_related(
            "sender", "listing__vehicle__make", "listing__vehicle__model"
        )


class InquiryReceivedListView(generics.ListAPIView):
    """List inquiries received by the authenticated user (seller)."""

    serializer_class = InquiryListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Inquiry.objects.filter(recipient=self.request.user).select_related(
            "sender", "listing__vehicle__make", "listing__vehicle__model"
        )


class InquiryDetailView(generics.RetrieveAPIView):
    """View a single inquiry."""

    serializer_class = InquiryDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Inquiry.objects.filter(
            models__sender=user
        ).select_related("sender", "recipient", "listing__vehicle__make", "listing__vehicle__model") | Inquiry.objects.filter(
            recipient=user
        ).select_related("sender", "recipient", "listing__vehicle__make", "listing__vehicle__model")

    def get_queryset(self):
        from django.db.models import Q

        user = self.request.user
        return Inquiry.objects.filter(
            Q(sender=user) | Q(recipient=user)
        ).select_related(
            "sender", "recipient", "listing__vehicle__make", "listing__vehicle__model"
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Mark as read if the recipient is viewing
        if instance.recipient == request.user and instance.status == Inquiry.Status.NEW:
            instance.status = Inquiry.Status.READ
            instance.save(update_fields=["status", "updated_at"])
        return super().retrieve(request, *args, **kwargs)


class InquiryReplyView(APIView):
    """Reply to an inquiry (seller only)."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            inquiry = Inquiry.objects.get(pk=pk, recipient=request.user)
        except Inquiry.DoesNotExist:
            return Response(
                {"detail": "Inquiry not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = InquiryReplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        inquiry.reply_message = serializer.validated_data["reply_message"]
        inquiry.replied_at = timezone.now()
        inquiry.status = Inquiry.Status.REPLIED
        inquiry.save(update_fields=["reply_message", "replied_at", "status", "updated_at"])

        return Response(
            InquiryDetailSerializer(inquiry).data, status=status.HTTP_200_OK
        )


class TestDriveRequestCreateView(generics.CreateAPIView):
    """Request a test drive for a listing."""

    serializer_class = TestDriveRequestCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class TestDriveRequestListView(generics.ListAPIView):
    """List test drive requests for the authenticated user."""

    serializer_class = TestDriveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from django.db.models import Q

        user = self.request.user
        return TestDriveRequest.objects.filter(
            Q(requester=user) | Q(dealer=user)
        ).select_related(
            "requester", "listing__vehicle__make", "listing__vehicle__model"
        )


class TestDriveRequestDetailView(generics.RetrieveUpdateAPIView):
    """View or update a test drive request."""

    serializer_class = TestDriveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from django.db.models import Q

        user = self.request.user
        return TestDriveRequest.objects.filter(
            Q(requester=user) | Q(dealer=user)
        ).select_related(
            "requester", "listing__vehicle__make", "listing__vehicle__model"
        )
