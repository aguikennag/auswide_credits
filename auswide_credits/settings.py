
import dj_database_url
from django.utils.timezone import timedelta
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SITE_NAME = "CommonWealth Credit"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'h0eantw*e!)@@!q@&)j5k1!znc#m66&^-)349#4%+_=_@(822^'


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'
MAINTENANCE_MODE = False

ALLOWED_HOSTS = ['*']

TEST_MODE = True


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
    'IDLE_TIME': timedelta(minutes=60),
    'REDIRECT_TO_LOGIN_IMMEDIATELY': True,
    'SESSION_TIME': timedelta(hours=1),
    'MESSAGE': 'Your session has expired. Please login again to continue.',
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
    
    #3rdparty
    'whitenoise.runserver_nostatic',

    'crispy_forms',
    'crispy_bootstrap4',
    'djmoney',
     #'phonenumber_field',

]


JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "Common Credit Admin",

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "Common Credit",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "Common Credit",

    # Logo to use for your site, must be present in static files, used for brand on top left
    "site_logo": "img/logo.png",

    # Logo to use for your site, must be present in static files, used for login form logo (defaults to site_logo)
    "login_logo": "img/logo-jazz.png",

    # Logo to use for login form in dark themes (defaults to login_logo)
    "login_logo_dark": "img/logo-jazz.png",

    # CSS classes that are applied to the logo above
    "site_logo_classes": "logo",

    "custom_css": "css/style.css",

    # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
    #"site_icon": "img/favicon.png",

    # Welcome text on the login screen
    "welcome_sign": "Welcome Admin!",

    # Copyright on the footer
    "copyright": "Common Credit",
}




CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # whitenoise
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'auswide_credits.middleware.AccountManagementMiddleware',
    'auswide_credits.middleware.MaintenanceMideMiddleware',
    'django_auto_logout.middleware.auto_logout',
    # language translation
    # 'django.middleware.locale.LocalMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'auswide_credits.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'users/templates/dashboard'),
            os.path.join(BASE_DIR, 'templates/email'),
            os.path.join(BASE_DIR, 'users/templates/registration'),
            os.path.join(BASE_DIR, 'wallet/templates'),
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

WSGI_APPLICATION = 'auswide_credits.wsgi.application'


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

#LANGUAGE_CODE = 'es'

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
TWILLO_ACCOUNT_SID = ''
TWILLO_AUTH_TOKEN = ''
SMS_PHONE_NUMBER = ''


#GODADDY and tawkto and zoho
#username : hmdzhamad@gmail.com
#email :hmdzhamad@gmail.com
# password : #@Hamadzz

#NAMECHEAP USERNAME
#username :  hmdzhamad8080
#password :  #@Hamadzz8080
#email : tammimrobbinson@gmail.com


# EMAIL FOR ZOHO
EMAIL_HOST = "smtp.zoho.com"
EMAIL_HOST_USER_SUPPORT = "support@commonwealthscredit.com"
EMAIL_HOST_USER_TRANSACTION = "transaction@commonwealthscredit.com"

# for other emails
EMAIL_HOST_USER = "support@commonwealthscredit.com"
DEFAULT_FROM_EMAIL = "support@commonwealthscredit.com"

EMAIL_HOST_PASSWORD = "#PoloK90We)("

EMAIL_PORT = "587"
EMAIL_USE_TLS = "True"
#EMAIL_USE_SSL = "False"

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
