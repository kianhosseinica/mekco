"""
Django settings for lightspeed project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-60)#2t!*97*m*%dk5way(fv=om4vh5_-aax@h(qj$90ojy!quf'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []
LIGHTSPEED_ACCOUNT_ID = '292471'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'oauth_handler',
    'ecommerce',
    'customers',
    'ecommerce.templatetags.custom_filters',

]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]


SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


ROOT_URLCONF = 'lightspeed.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'ecommerce.context_processors.cart_summary',

                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'lightspeed.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 50  # Set timeout to 30 seconds
        }
    }
}



# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CLIENT_ID = '26f227ea0348689a3b2f1300c6423999490230c6fe9205ea66d03cdfa5f565a8'
CLIENT_SECRET = '74d32fa89cd49c07bcb0a3d1b6d3fa40dd935ebd15b9d4486d0aeb8cd7282fa9'
REFRESH_TOKEN = 'd3c39b44972b45bc6ba2c65f816dce2fae02df2a'
ACCESS_TOKEN = None  # This will be set by the refresh token process




# EMAIL_BACKEND = 'oauth_handler.custom_email_backend.CustomEmailBackend'
# EMAIL_HOST = 'smtp.ionos.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_USE_SSL = False
# EMAIL_HOST_USER = 'orders@mekcosupply.com'  # Ensure this is your correct email address
# EMAIL_HOST_PASSWORD = 'Siavash@2020?!'  # Ensure this is your correct email password
# DEFAULT_FROM_EMAIL = 'orders@mekcosupply.com'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'mekcosupply@gmail.com'
EMAIL_HOST_PASSWORD = 'dasa yfky qjez wrgl'  # Use the app password if 2-step verification is enabled
DEFAULT_FROM_EMAIL = 'mekcosupply@gmail.com'





import os
import certifi
LOGIN_URL = '/customers/login/'

os.environ['SSL_CERT_FILE'] = certifi.where()
AUTH_USER_MODEL = 'customers.Customer'

AUTHENTICATION_BACKENDS = [
    'customers.backends.EmailOrPhoneBackend',
    'django.contrib.auth.backends.ModelBackend',
]




# settings.py
PAYPAL_CLIENT_ID = 'AaHk2fAqztEFCH4pDQa9TceDQ3f8L9CbYIFSCjEMLoZTatBjUvMnWxYP7yBiu7t0Y9VU3KdYKko2nsxu'
PAYPAL_SECRET_KEY = 'ELQMpzy3eUNZVVBFpiCzdusj7LwiV6ykZwE72HOWIAyakZfBEbGDiyg9ukTz38ikTPtbg8VrDu98fWyQ'
PAYPAL_MODE = 'sandbox'  # 'sandbox' or 'live'



