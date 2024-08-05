# flake8: noqa
import certifi
import os
import logging
from pathlib import Path

import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType
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
    'services.apps.ServicesConfig'
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

LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'comps:index'

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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - '
           '%(filename)s.%(funcName)s(%(lineno)d) - %(message)s'
)

ROOT_CA_CERT = BASE_DIR / os.getenv('ROOT_CA_CERT', 'RootCA.pem')
if ROOT_CA_CERT.exists():
    cacert_path = certifi.where()

    with open(cacert_path, 'r+') as original_cacert:
        original_certificates = original_cacert.read()

        with open(ROOT_CA_CERT, 'r') as root_ca:
            root_ca_certificate = root_ca.read()

            if root_ca_certificate not in original_certificates:
                original_cacert.write('\n# RootCA\n')
                original_cacert.write(root_ca_certificate)


INTERMEDIATE_CERT = BASE_DIR / os.getenv('INTERMEDIATE_CERT', 'Intermediate.pem')
if INTERMEDIATE_CERT.exists():
    cacert_path = certifi.where()

    with open(cacert_path, 'r+') as original_cacert:
        original_certificates = original_cacert.read()

        with open(INTERMEDIATE_CERT, 'r') as intermediate:
            intermediate_certificate = intermediate.read()

            if intermediate_certificate not in original_certificates:
                original_cacert.write('\n# Intermediate certificate\n')
                original_cacert.write(intermediate_certificate)

# Ключ для шифрования паролей сервисов
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')

# Настройки для авторизации по LDAP
AUTH_LDAP_SERVER_URI = f'ldap://{os.getenv("AUTH_LDAP_SERVER_URI")}'
AUTH_LDAP_BIND_DN = os.getenv('AUTH_LDAP_BIND_DN')
AUTH_LDAP_BIND_PASSWORD = os.getenv('AUTH_LDAP_BIND_PASSWORD')
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    os.getenv('AUTH_LDAP_USER_SEARCH'),
    ldap.SCOPE_SUBTREE, '(sAMAccountName=%(user)s)'
)
AUTH_LDAP_GROUP = os.getenv('AUTH_LDAP_GROUP_SEARCH')
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    AUTH_LDAP_GROUP,
    ldap.SCOPE_SUBTREE,
    '(objectClass=groupOfNames)'
)
AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr='cn')
AUTH_LDAP_REQUIRE_GROUP = AUTH_LDAP_GROUP
AUTH_LDAP_USER_ATTR_MAP = {
    'first_name': 'givenName',
    'last_name': 'sn',
    'email': 'mail'
}
AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    'is_active': AUTH_LDAP_GROUP,
    'is_staff': AUTH_LDAP_GROUP,
}
AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_FIND_GROUP_PERMS = True
AUTH_LDAP_CACHE_TIMEOUT = 3600
AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)
