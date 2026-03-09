"""
URL patterns for the accounts app.
"""

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("token/refresh/", views.TokenRefreshApiView.as_view(), name="token-refresh"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/password/", views.ChangePasswordView.as_view(), name="change-password"),
    path("profile/buyer/", views.BuyerProfileView.as_view(), name="buyer-profile"),
    path("dealers/", views.DealerListView.as_view(), name="dealer-list"),
    path("dealers/<uuid:pk>/", views.DealerDetailView.as_view(), name="dealer-detail"),
]
