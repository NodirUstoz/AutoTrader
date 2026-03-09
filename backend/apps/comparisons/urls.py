"""
URL patterns for the comparisons app.
"""

from django.urls import path

from . import views

app_name = "comparisons"

urlpatterns = [
    path("", views.ComparisonCreateView.as_view(), name="comparison-create"),
    path("mine/", views.MyComparisonsView.as_view(), name="my-comparisons"),
    path("<uuid:pk>/", views.ComparisonDetailView.as_view(), name="comparison-detail"),
    path(
        "<uuid:pk>/add/",
        views.ComparisonAddVehicleView.as_view(),
        name="comparison-add-vehicle",
    ),
    path(
        "<uuid:pk>/remove/",
        views.ComparisonRemoveVehicleView.as_view(),
        name="comparison-remove-vehicle",
    ),
]
