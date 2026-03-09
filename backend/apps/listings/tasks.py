"""
Celery tasks for the listings app.
"""

import logging

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count, F
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def expire_stale_listings(self):
    """
    Move listings past their expiry date to 'expired' status.
    Runs daily via celery-beat.
    """
    from .models import Listing

    now = timezone.now()
    expired = Listing.objects.filter(
        status=Listing.Status.ACTIVE,
        expires_at__lte=now,
    ).update(status=Listing.Status.EXPIRED)

    logger.info("Expired %d stale listings.", expired)
    return expired


@shared_task(bind=True, max_retries=3)
def send_saved_search_notifications(self):
    """
    Check each active saved search for new matching listings and
    send email notifications.
    """
    from .models import Listing, SavedSearch
    from apps.vehicles.models import Vehicle

    now = timezone.now()
    searches = SavedSearch.objects.filter(is_active=True, notify_email=True).select_related("user")

    notification_count = 0

    for saved_search in searches:
        # Skip if notified recently according to frequency
        if saved_search.last_notified_at:
            if saved_search.notify_frequency == "daily":
                cutoff = saved_search.last_notified_at + timezone.timedelta(hours=23)
            elif saved_search.notify_frequency == "weekly":
                cutoff = saved_search.last_notified_at + timezone.timedelta(days=6)
            else:
                cutoff = saved_search.last_notified_at  # instant
            if now < cutoff:
                continue

        # Build queryset from stored filters
        filters = saved_search.filters
        listings_qs = Listing.objects.filter(status=Listing.Status.ACTIVE)

        since = saved_search.last_notified_at or saved_search.created_at
        listings_qs = listings_qs.filter(published_at__gte=since)

        if "make_name" in filters:
            listings_qs = listings_qs.filter(vehicle__make__name__iexact=filters["make_name"])
        if "model_name" in filters:
            listings_qs = listings_qs.filter(vehicle__model__name__icontains=filters["model_name"])
        if "year_min" in filters:
            listings_qs = listings_qs.filter(vehicle__year__gte=filters["year_min"])
        if "year_max" in filters:
            listings_qs = listings_qs.filter(vehicle__year__lte=filters["year_max"])
        if "price_min" in filters:
            listings_qs = listings_qs.filter(price__gte=filters["price_min"])
        if "price_max" in filters:
            listings_qs = listings_qs.filter(price__lte=filters["price_max"])

        count = listings_qs.count()
        if count > 0:
            try:
                send_mail(
                    subject=f"AutoTrader: {count} new listing(s) matching '{saved_search.name}'",
                    message=(
                        f"Hi {saved_search.user.first_name},\n\n"
                        f"We found {count} new listing(s) matching your saved search "
                        f"'{saved_search.name}'.\n\n"
                        f"Visit AutoTrader to check them out!\n\n"
                        f"Best,\nAutoTrader Team"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[saved_search.user.email],
                    fail_silently=False,
                )
                notification_count += 1
            except Exception as exc:
                logger.error(
                    "Failed to send saved search notification to %s: %s",
                    saved_search.user.email,
                    exc,
                )

            saved_search.last_notified_at = now
            saved_search.save(update_fields=["last_notified_at"])

    logger.info("Sent %d saved search notifications.", notification_count)
    return notification_count


@shared_task(bind=True, max_retries=3)
def update_listing_statistics(self):
    """
    Recalculate aggregate statistics for listings.
    Ensures inquiry counts are in sync with the actual inquiry table.
    """
    from .models import Listing
    from apps.inquiries.models import Inquiry

    listings = Listing.objects.filter(status=Listing.Status.ACTIVE).annotate(
        actual_inquiry_count=Count("inquiries")
    )

    updated = 0
    for listing in listings:
        if listing.inquiries_count != listing.actual_inquiry_count:
            listing.inquiries_count = listing.actual_inquiry_count
            listing.save(update_fields=["inquiries_count"])
            updated += 1

    logger.info("Updated statistics for %d listings.", updated)
    return updated
