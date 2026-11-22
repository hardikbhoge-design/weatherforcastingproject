"""
Django settings for weather_forecast_ai project.
"""

from pathlib import Path
import os
import sys
import shutil

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Ensure project root and backend are in sys.path
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / 'backend'))

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-weather-ai-super-secret-key-for-forecasting-v2'

DEBUG = True

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['https://*.vercel.app']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'forecast.apps.ForecastConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
]
try:
    import whitenoise
    MIDDLEWARE.append('whitenoise.middleware.WhiteNoiseMiddleware')
except ImportError:
    pass

MIDDLEWARE.extend([
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
])

ROOT_URLCONF = 'weather_forecast_ai.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'frontend' / 'templates',
            BASE_DIR / 'backend' / 'forecast' / 'templates',
        ],
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

WSGI_APPLICATION = 'weather_forecast_ai.wsgi.application'

# Database configuration with Vercel / serverless environment support
IS_VERCEL = 'VERCEL' in os.environ

if IS_VERCEL:
    tmp_db = Path('/tmp') / 'db.sqlite3'
    orig_db = BASE_DIR / 'database' / 'db.sqlite3'
    if orig_db.exists() and not tmp_db.exists():
        try:
            shutil.copy2(orig_db, tmp_db)
        except Exception:
            pass
    DB_PATH = tmp_db
else:
    DB_PATH = BASE_DIR / 'database' / 'db.sqlite3'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_PATH,
    }
}

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    d for d in [
        BASE_DIR / 'frontend' / 'static',
        BASE_DIR / 'backend' / 'forecast' / 'static',
    ] if d.exists()
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Directory for cached ML models
if IS_VERCEL:
    ML_MODELS_DIR = Path('/tmp') / 'ml_models'
    try:
        os.makedirs(ML_MODELS_DIR, exist_ok=True)
        bundled_dir = BASE_DIR / 'backend' / 'forecast' / 'ml_models'
        if bundled_dir.exists():
            for f in bundled_dir.glob('*.joblib'):
                dest_file = ML_MODELS_DIR / f.name
                if not dest_file.exists():
                    shutil.copy2(f, dest_file)
    except Exception:
        pass
else:
    ML_MODELS_DIR = BASE_DIR / 'backend' / 'forecast' / 'ml_models'
    try:
        os.makedirs(ML_MODELS_DIR, exist_ok=True)
    except Exception:
        pass

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

