from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from church.models import Event, Notification, CustomUser

class Command(BaseCommand):
    help = 'Send in-app notifications for upcoming events (1 hour before start time)'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        upcoming_time = now + timedelta(hours=1)

        events = Event.objects.filter(start_datetime__range=(now, upcoming_time))

        for event in events:
            sent_to = []

            # First try all church admins linked directly via CustomUser.church
            church_admins = CustomUser.objects.filter(
                is_church_admin=True,
                church=event.church
            )

            if not church_admins.exists() and event.church.admin:
                # Fallback to church.admin if no admins are found via FK
                church_admins = [event.church.admin]

            for admin in church_admins:
                # Skip if notification already exists for this event & user
                if Notification.objects.filter(user=admin, event=event).exists():
                    continue

                Notification.objects.create(
                    user=admin,
                    church=event.church,
                    event=event,
                    message=f"The event '{event.title}' will start at {event.start_datetime.strftime('%H:%M %p')}.",
                )
                sent_to.append(admin.email if admin.email else str(admin))

            if sent_to:
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Notification sent for '{event.title}' to: {', '.join(sent_to)}"
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f"⚠️ No eligible admin found for event '{event.title}' ({event.church})"
                ))
