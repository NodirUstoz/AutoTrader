"""
URL patterns for the vehicles app.
"""

from django.urls import path

from . import views

app_name = "vehicles"

urlpatterns = [
    path("", views.VehicleListView.as_view(), name="vehicle-list"),
    path("create/", views.VehicleCreateView.as_view(), name="vehicle-create"),
    path("mine/", views.MyVehiclesView.as_view(), name="my-vehicles"),
    path("<uuid:pk>/", views.VehicleDetailView.as_view(), name="vehicle-detail"),
    path(
        "<uuid:vehicle_id>/images/",
        views.VehicleImageUploadView.as_view(),
        name="vehicle-image-upload",
    ),
    path("makes/", views.VehicleMakeListView.as_view(), name="make-list"),
    path("models/", views.VehicleModelListView.as_view(), name="model-list"),
    path("features/", views.VehicleFeatureListView.as_view(), name="feature-list"),
    path("vin/<str:vin>/", views.VINDecodeView.as_view(), name="vin-decode"),
]
