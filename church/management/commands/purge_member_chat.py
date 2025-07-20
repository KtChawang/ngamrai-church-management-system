from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from church.models import MemberChatMessage

class Command(BaseCommand):
    help = "Mark member chat messages older than 7 days as deleted."

    def handle(self, *args, **kwargs):
        cutoff = timezone.now() - timedelta(days=7)
        old_messages = MemberChatMessage.objects.filter(
            sent_at__lt=cutoff, is_deleted=False
        )
        count = old_messages.update(is_deleted=True)
        self.stdout.write(self.style.SUCCESS(f"✅ Marked {count} messages as deleted."))
