import dj_database_url
from django.utils.timezone import timedelta
import os


SITE_NAME = "Auswide Credits"

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'nc@ty7fx4rv2a8j7nkd-7$d1$^-s$5o#37b!6qv0uh@nok$c2o'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

TEST_MODE = True

JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "Auswide Credits Admin",

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "Auswide Credits",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "Auswide Credits",

    # Logo to use for your site, must be present in static files, used for brand on top left
    "site_logo": "img/logo.png",

    # Logo to use for your site, must be present in static files, used for login form logo (defaults to site_logo)
    "login_logo": "img/logo/logo-jazz.png",

    # Logo to use for login form in dark themes (defaults to login_logo)
    "login_logo_dark": "img/logo/logo-jazz.png",

    # CSS classes that are applied to the logo above
    "site_logo_classes": "logo",

    "custom_css": "css/style.css",

    # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
    # "site_icon": "img/favicon.png",

    # Welcome text on the login screen
    "welcome_sign": "Welcome Admin!",

    # Copyright on the footer
    "copyright": "Auswide Credits",
}


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO"},
    },
}


AUTO_LOGOUT = {
    'IDLE_TIME': timedelta(minutes=5),
    'REDIRECT_TO_LOGIN_IMMEDIATELY': True,
    'SESSION_TIME': timedelta(hours=1),
    'MESSAGE': 'Welcome back, your previous session expired !',
}  # logout after 10 minutes of downtime
# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users.apps.UsersConfig',
    'wallet.apps.WalletConfig',
    'company.apps.CompanyConfig',
    'core.apps.CoreConfig',
    # 3rdparty
    'whitenoise.runserver_nostatic',
    'crispy_forms',
    'crispy_bootstrap4',
    'djmoney'
    # 'phonenumber_field',

]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [

    # django
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',

    # whitenoise
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django_auto_logout.middleware.auto_logout',

    # language translation
    # 'django.middleware.locale.LocalMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # custom
    'online_bank.middleware.AccountMiddleware',

]

ROOT_URLCONF = 'online_bank.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'users/templates/dashboard'),
            os.path.join(BASE_DIR, 'templates/email'),
            os.path.join(BASE_DIR, 'templates/registration'),
            os.path.join(BASE_DIR, 'core/templates'),
            os.path.join(BASE_DIR, 'core/templates/email'),
        ],

        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                'core.context.core',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # auto logout
                'django_auto_logout.context_processors.auto_logout_client',
            ],
        },
    },
]

WSGI_APPLICATION = 'online_bank.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases


if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
            "OPTIONS": {
                "timeout": 30,
            }
        },
        "OPTIONS": {
            # ...
            "timeout": 30,
            # ...
        }
    }

else:
    # Replace the SQLite DATABASES configuration with PostgreSQL:

    DATABASES = {
        'default': dj_database_url.config(default='postgres://localhost:5432/mydatabase')
    }

# Password validation

# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGIN_REDIRECT_URL = 'dashboard'

LOGOUT_REDIRECT_URL = "index"

AUTH_USER_MODEL = 'users.User'

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

# LANGUAGE_CODE = 'es'

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'languages')
]

TIME_ZONE = 'UTC'


INTERNATIONAL_TRANSFER_CHARGE = 1

INTERNAL_TRANSFER_CHARGE = 1

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

MEDIA_URL = '/media/'


MEDIA_ROOT = os.path.join(BASE_DIR, "media")


STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]

STATIC_ROOT = os.path.join(BASE_DIR, "asset")

STATIC_URL = '/static/'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# TWILLO
TWILLO_ACCOUNT_SID = 'AC213bba1c05225bedc1ebccccd8dbd9e0'

TWILLO_AUTH_TOKEN = '8512ae91f275f2bf0c8bf864e61692f3'

SMS_PHONE_NUMBER = '+19709866198'


# EMAIL FOR ZOHO
EMAIL_HOST = "smtp.zoho.com"
EMAIL_HOST_USER_TRANSACTION = "alert@credocapitalbank.com"
EMAIL_HOST_USER_ALERT = "alert@credocapitalbank.com"
EMAIL_HOST_USER_SUPPORT = "support@credocapitalbank.com"

# for other emails
EMAIL_HOST_USER = "support@credocapitalbank.com"
DEFAULT_FROM_EMAIL = "support@credocapitalbank.com"
EMAIL_HOST_PASSWORD = '#@Kyletech99'

EMAIL_PORT = "587"
EMAIL_USE_TLS = "True"


# EMAIL FOR ZOHO
# EMAIL_HOST  = "smtp.zoho.com"
# EMAIL_HOST_USER_ALERT = "transactions@credofinancebank.com"
# EMAIL_HOST_USER_SUPPORT = "support@credofinancebank.com"

# for other emails
# EMAIL_HOST_USER = "support@credofinancebank.com"
# DEFAULT_FROM_EMAIL  = "support@credofinancebank.com"
# EMAIL_HOST_PASSWORD = '#Shawler200'

# EMAIL_PORT = "587"
# EMAIL_USE_TLS = "True"
# EMAIL_USE_SSL = "False"
