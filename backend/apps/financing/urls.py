"""
URL patterns for the financing app.
"""

from django.urls import path

from . import views

app_name = "financing"

urlpatterns = [
    path("calculate/", views.FinancingCalculateView.as_view(), name="calculate"),
    path("calculations/", views.MyCalculationsView.as_view(), name="my-calculations"),
    path("apply/", views.LoanApplicationCreateView.as_view(), name="loan-apply"),
    path("applications/", views.LoanApplicationListView.as_view(), name="loan-list"),
    path(
        "applications/<uuid:pk>/",
        views.LoanApplicationDetailView.as_view(),
        name="loan-detail",
    ),
]
