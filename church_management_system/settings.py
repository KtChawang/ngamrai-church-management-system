import dj_database_url
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env

FAST2SMS_API_KEY = os.getenv("FAST2SMS_API_KEY")


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-177odqy)l(gg5ogszudu&zsa^@)bs#zhg_l$e00fz@x^%277f%'
DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'ngamraicms.com',
    'www.ngamraicms.com',
    'church-management-system-asyl.onrender.com',
    'ngamrai-church-management-system.onrender.com',  # <-- this is missing!
]

AUTH_USER_MODEL = 'church.CustomUser'
LOGIN_URL = '/church-admin-login/'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'church',
    'chat',
    'widget_tweaks',

]

# Sessions last for 1 day (86400 seconds)
SESSION_COOKIE_AGE = 86400
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Optional but NOT required (handled dynamically via middleware)
# CHURCH_ADMIN_CSRF_COOKIE_NAME = 'churchadmin_csrftoken'
# CHURCH_ADMIN_SESSION_COOKIE_NAME = 'churchadmin_sessionid'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'church.middleware.ChurchAdminSessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'church_management_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'church_management_system.wsgi.application'
ASGI_APPLICATION = 'church_management_system.asgi.application'

import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True
    )
}

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTHENTICATION_BACKENDS = [
    'church.backends.EmailAuthBackend',
    'church.backends.PhoneNumberAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@churchsystem.com'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_TZ = True
USE_I18N = True

# Optional utility (not automatically used by Django, but can help if needed)
def get_session_cookie_name(request):
    if request.path.startswith('/church-admin'):
        return 'churchadmin_sessionid'
    return 'sessionid'


FAST2SMS_API_URL = "https://www.fast2sms.com/dev/bulkV2"
FAST2SMS_API_KEY = os.getenv("FAST2SMS_API_KEY")  # Load from .env
FAST2SMS_SENDER_ID = "FSTSMS"
FAST2SMS_ROUTE = "v3"



PAYMENT_UPI_ID = "your-upi-id@bank"
PAYMENT_QR_PATH = "images/payment_qr.png"  # Place in static folder
PAYMENT_INSTRUCTIONS = "After payment, contact support or wait for confirmation."



