"""
URL patterns for the inquiries app.
"""

from django.urls import path

from . import views

app_name = "inquiries"

urlpatterns = [
    path("", views.InquiryCreateView.as_view(), name="inquiry-create"),
    path("sent/", views.InquirySentListView.as_view(), name="inquiry-sent-list"),
    path("received/", views.InquiryReceivedListView.as_view(), name="inquiry-received-list"),
    path("<uuid:pk>/", views.InquiryDetailView.as_view(), name="inquiry-detail"),
    path("<uuid:pk>/reply/", views.InquiryReplyView.as_view(), name="inquiry-reply"),
    path("test-drives/", views.TestDriveRequestCreateView.as_view(), name="test-drive-create"),
    path("test-drives/list/", views.TestDriveRequestListView.as_view(), name="test-drive-list"),
    path(
        "test-drives/<uuid:pk>/",
        views.TestDriveRequestDetailView.as_view(),
        name="test-drive-detail",
    ),
]
