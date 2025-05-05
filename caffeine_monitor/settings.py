from pathlib import Path
import os
from dotenv import load_dotenv
import pymysql

# Load environment variables from a .env file if present
load_dotenv()

# Ensure that pymysql is used as MySQLdb (to fix MySQL compatibility)
pymysql.install_as_MySQLdb()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-(yxhfwe45#uj&%bpz5*o-6ibgo$pxmd7*b(&9#^+5!m5)xgg+%')  # Use environment variable for secret key

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'  # Set DEBUG from environment variable (default to True)

# Add your production domain in `ALLOWED_HOSTS`
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "tamang-kape-01.onrender.com",
    os.getenv('RAILWAY_PRIVATE_DOMAIN', ''),  # Railway private domain for deployment
]

# CORS settings for allowing frontend access
CORS_ALLOW_ALL_ORIGINS = True

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'monitoring',  # Your app
    'rest_framework',  # For API functionality
    'corsheaders',  # CORS middleware
]

# CSRF settings for specific domains (adjust as needed)
CSRF_TRUSTED_ORIGINS = [
    "http://10.0.2.2:8000",  # Allow requests from Flutter emulator
    os.getenv('FRONTEND_URL', ''),  # Frontend URL (e.g., deployed app URL)
]

# Middleware settings
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'caffeine_monitor.urls'

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
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'caffeine_monitor.wsgi.application'

# Database configuration using environment variables
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'railway'),  # Default to 'railway' if not set
        'USER': os.getenv('DB_USER', 'root'),  # Default to 'root' if not set
        'PASSWORD': os.getenv('DB_PASSWORD', 'hiINxMBTnKlBogPhOJlqyfDtJgtyJTOT'),  # Default password if not set
        'HOST': os.getenv('DB_HOST', 'switchback.proxy.rlwy.net'),
        'PORT': os.getenv('DB_PORT', '17884'),
    }
}

# Password validation settings (you may adjust these for production)
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

# Localization settings (timezone and language settings)
LANGUAGE_CODE = 'en-us'
TIME_ZONE = "Asia/Manila"
USE_I18N = True
USE_TZ = True  # Ensure timezone support is enabled

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# If you are running in production, set DEBUG to False and handle any other settings appropriately
if not DEBUG:
    # Additional production settings can be placed here
    pass
