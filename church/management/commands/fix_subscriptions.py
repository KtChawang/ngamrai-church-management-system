# church/management/commands/fix_subscriptions.py

from django.core.management.base import BaseCommand
from django.db.models import Count
from church.models import Subscription

class Command(BaseCommand):
    help = "Fix duplicate subscriptions for each church"

    def handle(self, *args, **options):
        self.stdout.write("🔍 Checking for duplicate subscriptions...\n")

        duplicates = (
            Subscription.objects
            .values('church')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
        )

        if not duplicates:
            self.stdout.write("✅ No duplicates found.\n")
            return

        for entry in duplicates:
            subs = Subscription.objects.filter(church=entry['church']).order_by('-last_paid_at')
            to_keep = subs.first()
            to_delete = subs.exclude(id=to_keep.id)

            count_deleted = to_delete.count()
            to_delete.delete()
            self.stdout.write(f"🧹 Cleaned {count_deleted} duplicate(s) for Church ID {entry['church']}\n")

        self.stdout.write("✅ Done cleaning duplicates.\n")
