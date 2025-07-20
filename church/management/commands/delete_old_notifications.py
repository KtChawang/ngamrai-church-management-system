from django.core.management.base import BaseCommand
from church.models import Notification, Church

class Command(BaseCommand):
    help = 'Keep only the latest 3 notifications per church and delete the rest.'

    def handle(self, *args, **kwargs):
        for church in Church.objects.all():
            old_notifications = list(
                Notification.objects.filter(church=church).order_by('-created_at')[3:]
            )
            count = len(old_notifications)
            for notification in old_notifications:
                notification.delete()
            self.stdout.write(f"✅ Deleted {count} old notifications for church: {church.church_name}")
