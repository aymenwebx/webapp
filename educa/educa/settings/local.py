from .base import *

DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '172.20.10.4', '0.0.0.0']

# Use SQLite for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# SECRET_KEY = 'fmJDFJN5L5⁾l5E^LF8$LEfP"L5M:5M:FMZ:5EMF:sdmf:emf:z^"okp'
# Disable security settings for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0

# Add debug toolbar
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')