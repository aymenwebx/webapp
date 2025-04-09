import os
from pathlib import Path
from decouple import Config, RepositoryEnv
from django.urls import reverse_lazy

BASE_DIR = Path(__file__).resolve().parent.parent.parent
config = Config(RepositoryEnv(BASE_DIR / '.env'))
AUTH_USER_MODEL = 'accounts.User'


INSTALLED_APPS = [
    'accounts.apps.AccountsConfig',
    'courses.apps.CoursesConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'embed_video',
    'students',
    'teachers',
    'ckeditor',
    'redisboard',
    'rest_framework',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'accounts.middleware.UserTypeRedirectMiddleware',
    'courses.middleware.RequestMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'educa.urls'
WSGI_APPLICATION = 'educa.wsgi.application'

# Auth
LOGIN_REDIRECT_URL = reverse_lazy('student_course_list')
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
"""MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'"""

# DRF
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379',
    }
}

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Full',
        'height': 300,
        'width': '100%',
    },
    'table': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList'],
            ['Table', 'Link'],
            ['RemoveFormat', 'Source']
        ],
        'height': 300,
        'width': '100%',
    }
}

INTERNAL_IPS = ['127.0.0.1']
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# SECRET_KEY = 'fmJDFJN5L5⁾l5E^LF8$LEfP"L5M:5M:FMZ:5EMF:sdmf:emf:z^"okp'
