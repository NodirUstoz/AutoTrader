"""
Celery configuration for AutoTrader.

Autodiscovers tasks from all installed apps and configures periodic
task scheduling via celery-beat.
"""

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("autotrader")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

# ---------------------------------------------------------------------------
# Periodic tasks
# ---------------------------------------------------------------------------

app.conf.beat_schedule = {
    "expire-stale-listings": {
        "task": "apps.listings.tasks.expire_stale_listings",
        "schedule": crontab(hour=2, minute=0),  # Daily at 02:00 UTC
    },
    "send-saved-search-notifications": {
        "task": "apps.listings.tasks.send_saved_search_notifications",
        "schedule": crontab(hour="*/6", minute=0),  # Every 6 hours
    },
    "update-listing-statistics": {
        "task": "apps.listings.tasks.update_listing_statistics",
        "schedule": crontab(hour=3, minute=30),  # Daily at 03:30 UTC
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task that prints the current request info."""
    print(f"Request: {self.request!r}")
