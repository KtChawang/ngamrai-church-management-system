# church/mixins.py

from django.core.exceptions import PermissionDenied

class IsChurchMemberMixin:
    """Allows only users with Member profile to access."""
    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, 'member'):
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied("You must be a church member to access this page.")