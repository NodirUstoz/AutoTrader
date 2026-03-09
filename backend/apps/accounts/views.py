"""
Views for user registration, authentication, and profile management.
"""

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import BuyerProfile, DealerProfile
from .permissions import IsDealerUser, IsOwnerOrReadOnly
from .serializers import (
    BuyerProfileSerializer,
    ChangePasswordSerializer,
    DealerListSerializer,
    DealerProfileSerializer,
    DealerProfileUpdateSerializer,
    UserProfileUpdateSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Register a new user account."""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """Obtain JWT token pair (access + refresh)."""

    permission_classes = [permissions.AllowAny]


class TokenRefreshApiView(TokenRefreshView):
    """Refresh an access token using a valid refresh token."""

    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    """Blacklist the refresh token to log the user out."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"detail": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Successfully logged out."},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"detail": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the authenticated user's profile."""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UserProfileUpdateSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    """Change the authenticated user's password."""

    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.get_object()
        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response(
            {"detail": "Password updated successfully."},
            status=status.HTTP_200_OK,
        )


class DealerListView(generics.ListAPIView):
    """List all verified dealer profiles."""

    serializer_class = DealerListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = DealerProfile.objects.select_related("user").filter(
            user__is_active=True
        )
        city = self.request.query_params.get("city")
        state = self.request.query_params.get("state")
        verified = self.request.query_params.get("verified")

        if city:
            queryset = queryset.filter(city__icontains=city)
        if state:
            queryset = queryset.filter(state__iexact=state)
        if verified is not None:
            queryset = queryset.filter(is_verified=verified.lower() == "true")

        return queryset


class DealerDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or update a dealer profile."""

    queryset = DealerProfile.objects.select_related("user")
    permission_classes = [IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return DealerProfileUpdateSerializer
        return DealerProfileSerializer


class BuyerProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the authenticated buyer's profile."""

    serializer_class = BuyerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = BuyerProfile.objects.get_or_create(user=self.request.user)
        return profile
