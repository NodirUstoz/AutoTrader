"""
URL patterns for the listings app.
"""

from django.urls import path

from . import views

app_name = "listings"

urlpatterns = [
    path("", views.ListingListView.as_view(), name="listing-list"),
    path("create/", views.ListingCreateView.as_view(), name="listing-create"),
    path("mine/", views.MyListingsView.as_view(), name="my-listings"),
    path("<uuid:pk>/", views.ListingDetailView.as_view(), name="listing-detail"),
    path("<uuid:pk>/publish/", views.publish_listing, name="listing-publish"),
    path("<uuid:pk>/sold/", views.mark_listing_sold, name="listing-sold"),
    path("saved-searches/", views.SavedSearchListCreateView.as_view(), name="saved-search-list"),
    path(
        "saved-searches/<uuid:pk>/",
        views.SavedSearchDetailView.as_view(),
        name="saved-search-detail",
    ),
]
