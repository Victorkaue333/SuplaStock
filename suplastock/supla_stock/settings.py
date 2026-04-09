# =====================================================
# suplastock - CONFIGURAÃ‡Ã•ES DJANGO
# =====================================================
"""
ConfiguraÃ§Ãµes Django para SuplaStock.
Para produÃ§Ã£o, use settings_prod.py ou configure via .env
"""

from pathlib import Path
from decouple import config, Csv
import os
import sys
from urllib.parse import urlparse
from django.core.exceptions import ImproperlyConfigured
import dj_database_url

# Detecta execução na Railway logo no início para suportar defaults seguros.
RUNNING_ON_RAILWAY = bool(
    os.getenv('RAILWAY_PROJECT_ID')
    or os.getenv('RAILWAY_SERVICE_ID')
    or os.getenv('RAILWAY_ENVIRONMENT_ID')
)

# Comando atual (quando executado via manage.py).
CURRENT_MANAGE_COMMAND = ''
if len(sys.argv) > 1 and sys.argv[0].endswith('manage.py'):
    CURRENT_MANAGE_COMMAND = sys.argv[1].strip().lower()

# Comandos de gerenciamento executados em hooks de build/deploy
# que podem usar SECRET_KEY temporária sem abrir brecha no runtime.
SECRET_KEY_OPTIONAL_COMMANDS = {
    'collectstatic',
    'migrate',
    'showmigrations',
    'makemigrations',
    'ensure_default_categories',
    'ensure_bootstrap_admin',
}

# Apenas collectstatic pode ignorar enforcement de DB na Railway.
DB_OPTIONAL_COMMANDS = {'collectstatic'}

# Importar configuraÃ§Ãµes de caminhos centralizadas
from config.paths import (
    BASE_DIR, LOGS_DIR, DATA_DIR, CONFIG_DIR, 
    MEDIA_DIR, STATIC_DIR, STATICFILES_DIR, DATABASE_FILE
)

# ============================================
# CONFIGURAÃ‡ÃƒO BASE
# ============================================


def _parse_debug_flag(default=True):
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


def _extract_hostname(raw_value):
    """
    Extrai hostname de valores vindos de env em formatos variados:
    - dominio.com
    - https://dominio.com
    - dominio.com:8080
    - *.dominio.com (convertido para .dominio.com em ALLOWED_HOSTS)
    """
    value = (raw_value or '').strip()
    if not value:
        return ''

    if value == '*':
        return '*'

    if value.startswith('*.'):
        return f".{value[2:].lower().rstrip('.')}"

    if value.startswith('.'):
        return value.lower().rstrip('.')

    parsed = urlparse(value if '://' in value else f'//{value}')
    hostname = (parsed.hostname or '').strip().lower().rstrip('.')

    if hostname:
        return hostname

    # Fallback defensivo para entradas sem parse padrÃ£o.
    return value.split('/')[0].split(':')[0].strip().lower().rstrip('.')


def _normalize_csrf_origin(raw_value):
    """
    Garante origem no formato exigido pelo Django 4+:
    scheme://host (com suporte a wildcard em subdominio).
    """
    value = (raw_value or '').strip()
    if not value:
        return ''

    if value.startswith('http://') or value.startswith('https://'):
        parsed = urlparse(value)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc.lower()}"
        return ''

    if value.startswith('.'):
        value = f"*{value}"

    if value.startswith('*.'):
        return f"https://{value.lower().rstrip('/')}"

    host = _extract_hostname(value)
    if not host:
        return ''

    scheme = 'http' if host in {'localhost', '127.0.0.1'} else 'https'
    return f"{scheme}://{host}"


def _build_allowed_hosts():
    hosts = set()

    for raw_host in config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv()):
        host = _extract_hostname(raw_host)
        if host:
            hosts.add(host)

    # Host usado pelo healthcheck interno da Railway.
    hosts.add('healthcheck.railway.app')
    hosts.add('.up.railway.app')

    railway_public_domain = _extract_hostname(os.getenv('RAILWAY_PUBLIC_DOMAIN', '').strip())
    if railway_public_domain:
        hosts.add(railway_public_domain)

    railway_static_host = _extract_hostname(os.getenv('RAILWAY_STATIC_URL', '').strip())
    if railway_static_host:
        hosts.add(railway_static_host)

    return sorted(hosts)


def _build_csrf_trusted_origins():
    origins = []

    for raw_origin in config(
        'CSRF_TRUSTED_ORIGINS',
        default='http://localhost,http://127.0.0.1',
        cast=Csv(),
    ):
        origin = _normalize_csrf_origin(raw_origin)
        if origin:
            origins.append(origin)

    railway_public_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN', '').strip()
    if railway_public_domain:
        normalized_public_origin = _normalize_csrf_origin(railway_public_domain)
        if normalized_public_origin:
            origins.append(normalized_public_origin)
    else:
        origins.append('https://*.up.railway.app')

    railway_static_url = os.getenv('RAILWAY_STATIC_URL', '').strip()
    if railway_static_url:
        normalized_static_origin = _normalize_csrf_origin(railway_static_url)
        if normalized_static_origin:
            origins.append(normalized_static_origin)

    # Remove duplicados mantendo ordem.
    return list(dict.fromkeys(origins))


def _normalize_database_url(raw_value):
    """
    Normaliza DATABASE_URL vindo de variaveis de ambiente.
    Aceita valores com aspas e ignora placeholders literais.
    """
    value = (raw_value or '').strip()
    if not value:
        return ''

    # Alguns paineis salvam o valor literal com aspas (as vezes em camadas).
    while len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1].strip()

    # Placeholders literais comuns (ainda nao resolvidos pelo provider).
    unresolved_placeholders = {
        '${{Postgres.DATABASE_URL}}',
        '${Postgres.DATABASE_URL}',
        '$DATABASE_URL',
    }
    if value in unresolved_placeholders:
        return ''

    # Valores "vazios" comuns persistidos como string.
    if value.lower() in {"", "none", "null", "''", '""'}:
        return ''

    return value

# BASE_DIR jÃ¡ importado de config.paths

# Criar diretÃ³rio de logs se nÃ£o existir (jÃ¡ feito em paths.py)

# ============================================
# SEGURANÃ‡A
# ============================================

DJANGO_ENV = config(
    'DJANGO_ENV',
    default='production' if RUNNING_ON_RAILWAY else 'development',
).strip().lower()
IS_DEVELOPMENT = DJANGO_ENV == 'development'

# SECURITY WARNING: mantenha a secret key em segredo em produÃ§Ã£o!
SECRET_KEY = config('SECRET_KEY', default='').strip()
if not SECRET_KEY:
    if IS_DEVELOPMENT or CURRENT_MANAGE_COMMAND in SECRET_KEY_OPTIONAL_COMMANDS:
        SECRET_KEY = 'django-insecure-local-dev-only'
    else:
        raise ImproperlyConfigured(
            'SECRET_KEY Ã© obrigatÃ³ria fora do ambiente de desenvolvimento.'
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
ALLOWED_HOSTS = _build_allowed_hosts()

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = _build_csrf_trusted_origins()

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

# Custom User Model
AUTH_USER_MODEL = 'usuarios.Usuario'
LOGIN_URL = 'usuarios:login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'usuarios:login'

# Proteção contra brute force no login
LOGIN_THROTTLE_ENABLED = config('LOGIN_THROTTLE_ENABLED', default=True, cast=bool)
LOGIN_THROTTLE_MAX_ATTEMPTS = config('LOGIN_THROTTLE_MAX_ATTEMPTS', default=5, cast=int)
LOGIN_THROTTLE_MAX_ATTEMPTS_PER_IP = config('LOGIN_THROTTLE_MAX_ATTEMPTS_PER_IP', default=20, cast=int)
LOGIN_THROTTLE_WINDOW_SECONDS = config('LOGIN_THROTTLE_WINDOW_SECONDS', default=900, cast=int)
LOGIN_THROTTLE_LOCKOUT_SECONDS = config('LOGIN_THROTTLE_LOCKOUT_SECONDS', default=900, cast=int)

# ============================================
# MIDDLEWARE
# ============================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'usuarios.middleware.DailyReauthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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
            BASE_DIR / 'suplastock' / 'templates',
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

SKIP_RAILWAY_DB_ENFORCEMENT_FOR = DB_OPTIONAL_COMMANDS

DATABASE_URL_RAW = config('DATABASE_URL', default='')
DATABASE_URL = _normalize_database_url(DATABASE_URL_RAW)
DATABASE_URL_INVALID = False
DATABASE_URL_INVALID_REASON = ''
DATABASE_ENGINE = config('DATABASE_ENGINE', default='sqlite')

# Build de estaticos nao depende de banco; ignora DATABASE_URL nesse fluxo.
if CURRENT_MANAGE_COMMAND in SKIP_RAILWAY_DB_ENFORCEMENT_FOR:
    DATABASE_URL = ''

PGHOST = os.getenv('PGHOST', '').strip()
PGDATABASE = os.getenv('PGDATABASE', '').strip()
PGUSER = os.getenv('PGUSER', '').strip()
PGPASSWORD = os.getenv('PGPASSWORD', '').strip()
PGPORT = os.getenv('PGPORT', '5432').strip()

if DATABASE_URL:
    try:
        DATABASES = {
            'default': dj_database_url.parse(
                DATABASE_URL,
                conn_max_age=config('DATABASE_CONN_MAX_AGE', default=60, cast=int),
                ssl_require=config('DATABASE_SSL_REQUIRE', default=False, cast=bool),
            )
        }
    except Exception as exc:
        DATABASE_URL_INVALID = True
        DATABASE_URL_INVALID_REASON = str(exc)
        DATABASE_URL = ''
        DATABASES = {}
elif PGHOST and PGDATABASE and PGUSER:
    # Fallback Ãºtil para Railway quando variÃ¡veis PG* estiverem disponÃ­veis
    # e DATABASE_URL nÃ£o tiver sido configurada no serviÃ§o.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': PGDATABASE,
            'USER': PGUSER,
            'PASSWORD': PGPASSWORD,
            'HOST': PGHOST,
            'PORT': PGPORT or '5432',
        }
    }
elif DATABASE_ENGINE == 'postgresql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DATABASE_NAME', default='suplastock'),
            'USER': config('DATABASE_USER', default='postgres'),
            'PASSWORD': config('DATABASE_PASSWORD', default=''),
            'HOST': config('DATABASE_HOST', default='localhost'),
            'PORT': config('DATABASE_PORT', default='5432'),
        }
    }
elif DATABASE_ENGINE == 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': DATABASE_FILE,
        }
    }
else:
    DATABASES = {}

if not DATABASES:
    if PGHOST and PGDATABASE and PGUSER:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': PGDATABASE,
                'USER': PGUSER,
                'PASSWORD': PGPASSWORD,
                'HOST': PGHOST,
                'PORT': PGPORT or '5432',
            }
        }

if not DATABASES:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': DATABASE_FILE,
        }
    }

# Em comandos criticos na Railway, URL invalida tambem deve bloquear.
if (
    RUNNING_ON_RAILWAY
    and DATABASE_URL_INVALID
    and DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3'
    and CURRENT_MANAGE_COMMAND not in SKIP_RAILWAY_DB_ENFORCEMENT_FOR
):
    raise ImproperlyConfigured(
        "DATABASE_URL invalida na Railway: "
        + DATABASE_URL_INVALID_REASON
        + ". Defina DATABASE_URL com URL postgres valida."
    )

if (
    RUNNING_ON_RAILWAY
    and DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3'
    and CURRENT_MANAGE_COMMAND not in SKIP_RAILWAY_DB_ENFORCEMENT_FOR
):
    raise ImproperlyConfigured(
        "Railway requer PostgreSQL para persistencia. "
        "Configure DATABASE_URL (ou PGHOST/PGDATABASE/PGUSER) no servico da Railway."
    )

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
STATICFILES_DIRS = [STATIC_DIR]
STATIC_ROOT = STATICFILES_DIR

# WhiteNoise para servir arquivos estÃ¡ticos
# Em desenvolvimento, usar storage simples; em produÃ§Ã£o, usar manifest
if DEBUG:
    STORAGES = {
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    }
else:
    STORAGES = {
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

# ============================================
# ARQUIVOS DE MÃDIA
# ============================================

MEDIA_URL = '/media/'
MEDIA_ROOT = MEDIA_DIR

# Upload seguro de imagens de produto
PRODUTO_IMAGE_MAX_BYTES = config('PRODUTO_IMAGE_MAX_BYTES', default=5 * 1024 * 1024, cast=int)
PRODUTO_IMAGE_MAX_WIDTH = config('PRODUTO_IMAGE_MAX_WIDTH', default=4096, cast=int)
PRODUTO_IMAGE_MAX_HEIGHT = config('PRODUTO_IMAGE_MAX_HEIGHT', default=4096, cast=int)

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

# ============================================
# SESSÃƒO
# ============================================

SESSION_COOKIE_AGE = config('SESSION_COOKIE_AGE', default=12 * 60 * 60, cast=int)  # fallback: 12h
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

SECURE_SSL = config('SECURE_SSL', default=False, cast=bool)
if SECURE_SSL:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
else:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    X_FRAME_OPTIONS = 'SAMEORIGIN'

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
            },
            'KEY_PREFIX': 'suplastock',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }

# ============================================
# CORS
# ============================================

CORS_ALLOW_ALL_ORIGINS = config(
    'CORS_ALLOW_ALL_ORIGINS',
    default=False,
    cast=bool,
)
if not IS_DEVELOPMENT and CORS_ALLOW_ALL_ORIGINS:
    raise ImproperlyConfigured(
        'CORS_ALLOW_ALL_ORIGINS nÃ£o pode ser habilitado fora de desenvolvimento.'
    )

CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:8000,http://127.0.0.1:8000',
    cast=Csv(),
)
CORS_ALLOW_CREDENTIALS = True

# ============================================
# LOGGING
# ============================================

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
            'filename': LOGS_DIR / 'django.log',
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'errors.log',
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'gestao': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# ============================================
# CONFIGURAÃ‡Ã•ES ADICIONAIS
# ============================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Metadados globais da aplicaÃ§Ã£o (rodapÃ©)
APP_LAST_UPDATE = config('APP_LAST_UPDATE', default='').strip()
FOOTER_DEV_NAME = config('FOOTER_DEV_NAME', default='VK Software').strip()
FOOTER_DEV_URL = config(
    'FOOTER_DEV_URL',
    default='https://vk-software-site-institucional.vercel.app/',
).strip()

# Django Compressor
COMPRESS_ENABLED = not DEBUG
COMPRESS_ROOT = STATIC_ROOT


