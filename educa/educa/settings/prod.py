from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '172.20.10.4','172.20.10.5', '127.0.0.1', '154.121.119.30']

# PostgreSQL for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('postgre_db', default='educa'),
        'USER': config('postgre_user', default='educauser'),
        'PASSWORD': config('postgre_password', default='Exceed99*'),
        'HOST': 'localhost',
        'PORT': 5432,
}
}

# Security settings
SECRET_KEY = 'fmJDFJN5L5⁾l5E^LF8$LEfP"L5M:5M:FMZ:5EMF:sdmf:emf:z^"okp'

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = None

SECURE_HSTS_SECONDS = 0 # 31536000  # 1 year
"""
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
"""