# flake8: noqa
import certifi
import os
import logging
from pathlib import Path

from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY', 'Develop_KEY')
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    'rest_framework',
    'api.apps.ApiConfig',
    'comps.apps.CompsConfig',
    'users.apps.UsersConfig',
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

ROOT_URLCONF = 'invent_pc.urls'

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'comps.context_processors.year.year',
            ],
        },
    },
]

WSGI_APPLICATION = 'invent_pc.wsgi.application'

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_DB', 'django'),
            'USER': os.getenv('POSTGRES_USER', 'django'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', ''),
            'PORT': os.getenv('DB_PORT', 5432)
        }
    }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Asia/Novosibirsk'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'collected_static'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Версия API
API_VERSION = 'v1'

# Количество записей на странице пагинатора
COUNT_PAGES_PAGINATOR = os.getenv('COUNT_PER_PAGE', 20)
# Константа для определения уникальности мак-адреса
COUNT_MAC = 1
# Дельта для определения устаревшего олнайна компьютеров, в днях
DAYS_OFFLINE = 180

# Конфигурация подключения к AD
AD_STATUS_DISABLED_USER = (514, 66050)
AD = {
    'AD_HOST': os.getenv('AD_HOST'),
    'AD_DOMAIN': os.getenv('AD_DOMAIN'),
    'AD_USER': os.getenv('AD_USER'),
    'AD_PASSWORD': os.getenv('AD_PASSWORD'),
    'AD_SEARCH_BASE': os.getenv('AD_SEARCH_BASE'),
    'AD_SEARCH_FILTER': os.getenv('AD_SEARCH_FILTER')
}

# Конфигурация подключения к Mikrotik
VPN = {
    'VPN_HOST': os.getenv('VPN_HOST'),
    'VPN_USER': os.getenv('VPN_USER'),
    'VPN_PASSWORD': os.getenv('VPN_PASSWORD'),
    'VPN_USE_SSL': os.getenv('VPN_USE_SSL', 'False').lower() in ('true',),
    'VPN_SSL_VERIFY': os.getenv('VPN_SSL_VERIFY', 'False').lower() in ('true',),
    'VPN_SSL_VERIFY_HOSTNAME': os.getenv('VPN_SSL_VERIFY_HOSTNAME', 'False').lower() in ('true',),
    'VPN_NEED_DISABLE_USERS': os.getenv('VPN_NEED_DISABLE_USERS', 'False').lower() in ('true',)
}

# Конфигурация подключения к RADIUS
RADIUS = {
    'RADIUS_HOST': os.getenv('RADIUS_HOST'),
    'RADIUS_SCRIPT': os.getenv('RADIUS_SCRIPT'),
    'RADIUS_USER': os.getenv('RADIUS_USER'),
    'RADIUS_PASSWORD': os.getenv('RADIUS_PASSWORD'),
    'RADIUS_SERVER_CERT_VALIDATION': os.getenv('RADIUS_SERVER_CERT_VALIDATION'),
    'RADIUS_NEED_DISABLE_USERS': os.getenv('RADIUS_NEED_DISABLE_USERS', 'False').lower() in ('true',)
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - '
           '%(filename)s.%(funcName)s(%(lineno)d) - %(message)s'
)

ROOT_CA_CERT = BASE_DIR / os.getenv('ROOT_CA_CERT', 'RootCA.pem')
if ROOT_CA_CERT.exists():
    cacert_path = certifi.where()
    new_cacert_path = os.path.join(os.path.dirname(cacert_path), 'new_cacert.pem')

    with open(cacert_path, 'r') as original_cacert:
        original_certificates = original_cacert.read()

    with open(ROOT_CA_CERT, 'r') as root_ca:
        root_ca_certificate = root_ca.read()

    with open(new_cacert_path, 'w') as new_cacert:
        new_cacert.write(original_certificates)
        new_cacert.write(root_ca_certificate)

    os.environ['SSL_CERT_FILE'] = new_cacert_path
