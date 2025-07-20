# church/management/commands/delete_old_prayer_requests.py
from datetime import timedelta                     # ← add this
from django.core.management.base import BaseCommand
from django.utils import timezone

from church.models import PrayerRequest


class Command(BaseCommand):
    help = "Delete all prayer requests older than 24 hours"

    def handle(self, *args, **kwargs):
        cutoff = timezone.now() - timedelta(hours=24)   # ← use timedelta here
        old_prayers = PrayerRequest.objects.filter(created_at__lt=cutoff)
        count = old_prayers.count()
        old_prayers.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Successfully deleted {count} prayer request(s) older than 24 hours."
            )
        )
