from django.apps import AppConfig

class ChatConfig(AppConfig):
    name = 'chat'


def ready(self):
    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType
    Message = self.get_model("Message")
    content_type = ContentType.objects.get_for_model(Message)
    Permission.objects.get_or_create(
        codename="moderate_message",
        name="Can moderate chat messages",
        content_type=content_type,
    )