from django.utils.deprecation import MiddlewareMixin
from importlib import import_module
from django.conf import settings

engine = import_module(settings.SESSION_ENGINE)

class ChurchAdminSessionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        path = request.path

        # Use special cookie if accessing church admin dashboard
        if path.startswith('/church-admin') or path.startswith('/church/church-admin'):
            session_key = request.COOKIES.get('churchadmin_sessionid')
        else:
            session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)

        request.session = engine.SessionStore(session_key)
