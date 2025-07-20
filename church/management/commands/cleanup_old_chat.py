from datetime import timedelta
from django.utils import timezone
from church.models import MemberChatMessage

def delete_old_member_messages():
    cutoff = timezone.now() - timedelta(days=7)
    old_messages = MemberChatMessage.objects.filter(sent_at__lt=cutoff)
    count = old_messages.update(is_deleted=True)
    print(f"Marked {count} old messages as deleted.")
