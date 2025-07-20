from .models import Subscription
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import localtime
from django.utils import timezone  # ✅ REQUIRED for timezone.now()
from .models import Church, ChurchAdminProfile, Event, Notification
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=Church)
def create_church_admin_profile(sender, instance, created, **kwargs):
    if created and instance.admin:
        user = instance.admin
        if not ChurchAdminProfile.objects.filter(user=user).exists():
            ChurchAdminProfile.objects.create(
                user=user,
                church=instance,
                full_name=f"{user.first_name} {user.last_name}",
            )


@receiver(post_save, sender=Event)
def notify_admins_on_event_create(sender, instance, created, **kwargs):
    if created:
        church = instance.church
        admins = User.objects.filter(church=church, is_church_admin=True)
        for admin in admins:
            Notification.objects.create(
                user=admin,
                church=church,
                event=instance,
                message=f"New Event: {instance.title} on {localtime(instance.start_datetime).strftime('%b %d, %Y at %I:%M %p')}"
            )


@receiver(post_save, sender=Church)
def create_initial_subscription(sender, instance, created, **kwargs):
    """
    Whenever a new Church is created, ensure it has a Subscription.
    """
    if created and not Subscription.objects.filter(church=instance).exists():
        today = timezone.now().date()
        Subscription.objects.create(
            church=instance,
            plan="monthly",      # default plan
            amount=0,            # or your starter fee
            last_paid_at=today,
        )