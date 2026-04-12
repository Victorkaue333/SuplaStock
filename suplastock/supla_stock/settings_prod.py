# =====================================================
# suplastock - SETTINGS DE PRODUÃ‡ÃƒO
# =====================================================
"""
ConfiguraÃ§Ãµes Django para SuplaStock.
Suporta mÃºltiplos ambientes: development, staging, production
"""

from pathlib import Path
import os
from decouple import config, Csv
import sys
from django.core.exceptions import ImproperlyConfigured

# ============================================
# CONFIGURAÃ‡ÃƒO BASE
# ============================================

BASE_DIR = Path(__file__).resolve().parent.parent


def _parse_debug_flag(default=False):
    """
    Parseia DEBUG de forma tolerante para evitar quebra com valores inesperados
    (ex.: "release", "production").
    """
    raw_value = config('DEBUG', default=str(default))

    if isinstance(raw_value, bool):
        return raw_value

    normalized = str(raw_value).strip().lower()
    if normalized in {'1', 'true', 'yes', 'on'}:
        return True
    if normalized in {'0', 'false', 'no', 'off', 'release', 'prod', 'production'}:
        return False

    return default

# Ambiente atual
DJANGO_ENV = config('DJANGO_ENV', default='development')
IS_PRODUCTION = DJANGO_ENV == 'production'
IS_STAGING = DJANGO_ENV == 'staging'
IS_DEVELOPMENT = DJANGO_ENV == 'development'

# Comando atual (quando executado via manage.py).
CURRENT_MANAGE_COMMAND = ''
if len(sys.argv) > 1 and sys.argv[0].endswith('manage.py'):
    CURRENT_MANAGE_COMMAND = sys.argv[1].strip().lower()

SECRET_KEY_OPTIONAL_COMMANDS = {
    'collectstatic',
    'migrate',
    'showmigrations',
    'makemigrations',
    'ensure_default_categories',
    'ensure_bootstrap_admin',
}

# ============================================
# SEGURANÃ‡A
# ============================================

# SECURITY WARNING: mantenha a secret key em segredo em produÃ§Ã£o!
SECRET_KEY = config('SECRET_KEY', default='').strip()
if not SECRET_KEY:
    if IS_DEVELOPMENT or CURRENT_MANAGE_COMMAND in SECRET_KEY_OPTIONAL_COMMANDS:
        SECRET_KEY = 'django-insecure-local-dev-only'
    else:
        raise ImproperlyConfigured(
            'SECRET_KEY e obrigatoria fora do ambiente de desenvolvimento.'
        )

if (
    not IS_DEVELOPMENT
    and SECRET_KEY.startswith('django-insecure')
    and CURRENT_MANAGE_COMMAND not in SECRET_KEY_OPTIONAL_COMMANDS
):
    raise ImproperlyConfigured(
        'SECRET_KEY insegura detectada fora de desenvolvimento.'
    )

# SECURITY WARNING: nÃ£o execute com debug ligado em produÃ§Ã£o!
DEBUG = _parse_debug_flag(default=IS_DEVELOPMENT)
if not IS_DEVELOPMENT and DEBUG:
    raise ImproperlyConfigured(
        'DEBUG deve ser False fora do ambiente de desenvolvimento.'
    )

# Hosts permitidos
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# CSRF Trusted Origins (necessÃ¡rio para Django 4.0+)
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='http://localhost,http://127.0.0.1', cast=Csv())

# ============================================
# APLICAÃ‡Ã•ES
# ============================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Apps de terceiros
    'corsheaders',
    'compressor',
    'health_check',
    'health_check.db',
    'health_check.cache',
    'health_check.storage',
    
    # Apps do projeto
    'dashboard',
    'usuarios',
    'estoque',
    'vendas',
    'financeiro',
]

# ============================================
# MODELO DE USUÃRIO CUSTOMIZADO
# ============================================

AUTH_USER_MODEL = 'usuarios.Usuario'

# ============================================
# MIDDLEWARE
# ============================================

MIDDLEWARE = [
    # SeguranÃ§a primeiro
    'django.middleware.security.SecurityMiddleware',
    
    # WhiteNoise para arquivos estÃ¡ticos (antes de tudo, exceto seguranÃ§a)
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
    # CORS
    'corsheaders.middleware.CorsMiddleware',
    
    # Django padrÃ£o
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'usuarios.middleware.DailyReauthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Rate limiting
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    
]

ROOT_URLCONF = 'suplastock.urls'

# ============================================
# TEMPLATES
# ============================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'supla_stock' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'suplastock.context_processors.footer_metadata',
            ],
        },
    },
]

WSGI_APPLICATION = 'suplastock.wsgi.application'

# ============================================
# BANCO DE DADOS
# ============================================

DATABASE_ENGINE = config('DATABASE_ENGINE', default='sqlite')

if DATABASE_ENGINE == 'postgresql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DATABASE_NAME', default='suplastock'),
            'USER': config('DATABASE_USER', default='postgres'),
            'PASSWORD': config('DATABASE_PASSWORD', default=''),
            'HOST': config('DATABASE_HOST', default='localhost'),
            'PORT': config('DATABASE_PORT', default='5432'),
            'CONN_MAX_AGE': 60,
            'OPTIONS': {
                'connect_timeout': 10,
            },
        }
    }
elif DATABASE_ENGINE == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config('DATABASE_NAME', default='suplastock'),
            'USER': config('DATABASE_USER', default='root'),
            'PASSWORD': config('DATABASE_PASSWORD', default=''),
            'HOST': config('DATABASE_HOST', default='localhost'),
            'PORT': config('DATABASE_PORT', default='3306'),
            'CONN_MAX_AGE': 60,
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    # SQLite (apenas para desenvolvimento)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ============================================
# VALIDAÃ‡ÃƒO DE SENHA
# ============================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ============================================
# INTERNACIONALIZAÃ‡ÃƒO
# ============================================

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# ============================================
# ARQUIVOS ESTÃTICOS
# ============================================

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise para servir arquivos estÃ¡ticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Django Compressor
COMPRESS_ENABLED = not DEBUG
COMPRESS_ROOT = STATIC_ROOT

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

# ============================================
# ARQUIVOS DE MÃDIA
# ============================================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Storage S3 (opcional para produÃ§Ã£o)
STORAGE_BACKEND = config('STORAGE_BACKEND', default='local')

if STORAGE_BACKEND == 's3' and IS_PRODUCTION:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='sa-east-1')
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_QUERYSTRING_AUTH = False

# ============================================
# AUTENTICAÃ‡ÃƒO
# ============================================

LOGIN_URL = 'usuarios:login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'usuarios:login'

# ============================================
# EMAIL
# ============================================

EMAIL_BACKEND_TYPE = config('EMAIL_BACKEND', default='console')

if EMAIL_BACKEND_TYPE == 'smtp':
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@suplastock.com')
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# ============================================
# SESSÃƒO
# ============================================

SESSION_COOKIE_AGE = config('SESSION_COOKIE_AGE', default=12 * 60 * 60, cast=int)  # fallback: 12h
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

if config('SECURE_SSL', default=False, cast=bool):
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# ============================================
# CACHE
# ============================================

CACHE_BACKEND_TYPE = config('CACHE_BACKEND', default='dummy')

if CACHE_BACKEND_TYPE == 'redis':
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': config('REDIS_URL', default='redis://localhost:6379/0'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {'max_connections': 50},
                'SOCKET_CONNECT_TIMEOUT': 5,
                'SOCKET_TIMEOUT': 5,
            },
            'KEY_PREFIX': 'suplastock',
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }

# ============================================
# SEGURANÃ‡A ADICIONAL (PRODUÃ‡ÃƒO)
# ============================================

if config('SECURE_SSL', default=False, cast=bool):
    # HTTPS
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    
    # HSTS
    SECURE_HSTS_SECONDS = 31536000  # 1 ano
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Outras configuraÃ§Ãµes de seguranÃ§a
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
else:
    SECURE_SSL_REDIRECT = False
    X_FRAME_OPTIONS = 'SAMEORIGIN'

# ============================================
# CORS
# ============================================

if IS_DEVELOPMENT:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='', cast=Csv())
    CORS_ALLOW_CREDENTIALS = True

# ============================================
# LOGGING
# ============================================

LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"level": "%(levelname)s", "time": "%(asctime)s", "module": "%(module)s", "message": "%(message)s"}',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'django.log',
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'errors.log',
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'security.log',
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['error_file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'usuarios': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'estoque': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'vendas': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'financeiro': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# ============================================
# SENTRY (MONITORAMENTO DE ERROS)
# ============================================

SENTRY_DSN = config('SENTRY_DSN', default='')

if SENTRY_DSN and not IS_DEVELOPMENT:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    
    sentry_logging = LoggingIntegration(
        level=None,
        event_level=None,
    )
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            sentry_logging,
        ],
        traces_sample_rate=0.1 if IS_PRODUCTION else 0.5,
        send_default_pii=False,
        environment=DJANGO_ENV,
    )

# ============================================
# RATE LIMITING
# ============================================

RATELIMIT_ENABLE = not IS_DEVELOPMENT
RATELIMIT_USE_CACHE = 'default'
RATELIMIT_FAIL_OPEN = True

# ============================================
# CONFIGURAÃ‡Ã•ES ADICIONAIS
# ============================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Admins para receber emails de erro
ADMINS = [
    ('Admin SuplaStock', config('ADMIN_EMAIL', default='admin@suplastock.com')),
]
MANAGERS = ADMINS

# ============================================
# HEALTH CHECK
# ============================================

HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,  # percent
    'MEMORY_MIN': 100,  # MB
}

# Metadados globais da aplicaÃƒÂ§ÃƒÂ£o (rodapÃƒÂ©)
APP_LAST_UPDATE = config('APP_LAST_UPDATE', default='').strip()
FOOTER_DEV_NAME = config('FOOTER_DEV_NAME', default='VK Software').strip()
FOOTER_DEV_URL = config(
    'FOOTER_DEV_URL',
    default='https://vk-software-site-institucional.vercel.app/',
).strip()

