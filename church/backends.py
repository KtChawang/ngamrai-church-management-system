# church/backends.py
from django.contrib.auth.backends import ModelBackend
from .models import CustomUser, Member

class EmailAuthBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(email=email)
            if user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None



class PhoneNumberAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Try to authenticate using phone number from Member
            member = Member.objects.get(phone_number=username)
            user = member.user
            if user.check_password(password):
                return user
        except Member.DoesNotExist:
            return None