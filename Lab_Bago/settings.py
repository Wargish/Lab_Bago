"""
Django settings for Lab_Bago project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# URL
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/home/'
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-6y0lrv#8id)*7+2&+@r&5=522d)mo159p=_bgi6f)2jvhu04f%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
    'authentication',
    'internal_workers',
    'external_workers',
    'sweetify',
    'axes',
    'django_recaptcha',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
]


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'axes.backends.AxesStandaloneBackend',
]




ROOT_URLCONF = 'Lab_Bago.urls'

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
                'app.context_processors.notificaciones',
                'app.context_processors.user_groups',

            ],
        },
    },
]

WSGI_APPLICATION = 'Lab_Bago.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,  # Contraseña de al menos 12 caracteres
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'app.validators.UppercaseValidator',  # Asegura al menos una mayúscula
    },
    {
        'NAME': 'app.validators.SpecialCharacterValidator',  # Asegura al menos un carácter especial
    },
]



# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = "America/Santiago"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
# Directorio donde se guardarán las imágenes
# Ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configuración de archivos multimedia (imágenes subidas por el usuario)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'app/static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')



# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# possible options: 'sweetalert', 'sweetalert2' - default is 'sweetalert2'
SWEETIFY_SWEETALERT_LIBRARY = 'sweetalert2'
# possible options: 'error', 'warning', 'info', 'question', 'success' - default is 'error'


# Configuración de correo en Django para usar Gmail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Servidor SMTP de Gmail
EMAIL_PORT = 587  # Puerto de Gmail para TLS
EMAIL_HOST_USER = 'bago.emailtest@gmail.com'  # Tu correo de Gmail
EMAIL_HOST_PASSWORD = 'orsn ouqw ktuj sxcv'  # La contraseña de la cuenta
EMAIL_USE_TLS = True  # Usamos TLS para mayor seguridad
DEFAULT_FROM_EMAIL = 'bago.emailtest@gmail.com'  # El correo que enviará los mensajes


# Key y Secret de Google reCAPTCHA
RECAPTCHA_PUBLIC_KEY = '6LcVpJoqAAAAAOY9_u-ep22mSQzIoPbDgbLk7Zrz'
RECAPTCHA_PRIVATE_KEY = '6LcVpJoqAAAAABuXx2QBkXgW_5EBYQi-twAj4gGt'
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']

# Intentos de inicio de sesión
AXES_ENABLED = True  # Habilitar protección contra intentos fallidos
AXES_FAILURE_LIMIT = 5  # Número de intentos fallidos antes de bloquear temporalmente
AXES_COOLOFF_TIME = 1  # Tiempo en horas que debe pasar antes de permitir nuevos intentos después del límite
AXES_LOCKOUT_BY_COMBINATION_USER_AND_IP = True  # Bloquear IP por usuario e IP combinados



# Seguridad
#SECURE_SSL_REDIRECT = True
#SECURE_HSTS_SECONDS = 31536000  # 1 año recomendado
#SECURE_HSTS_INCLUDE_SUBDOMAINS = True
#SECURE_HSTS_PRELOAD = True
#SECURE_BROWSER_XSS_FILTER = True
#SECURE_CONTENT_TYPE_NOSNIFF = True

# Cookies seguras
SESSION_COOKIE_SECURE = True
#CSRF_COOKIE_SECURE = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Cierra la sesión al cerrar el navegador

# Referer Policy
#SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"


# Configuración de LOGGING
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'security.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.security': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
}