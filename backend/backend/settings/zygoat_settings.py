"""
This settings file is generated and updated by Zygoat and should not be edited
manually. Instead, update settings via this package's __init__.py.
"""

import os
import json
import boto3
import environ

env = environ.Env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/
PRODUCTION = env.bool("DJANGO_PRODUCTION", default=False)


def get_secret(secret_arn):
    """Create a Secrets Manager client"""
    client = boto3.client("secretsmanager")
    get_secret_value_response = client.get_secret_value(SecretId=secret_arn)
    return get_secret_value_response


def prod_required_env(key, default, method="str"):
    """Throw an exception if PRODUCTION is true and key is not provided"""
    if PRODUCTION:
        default = environ.Env.NOTSET
    return getattr(env, method)(key, default)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = prod_required_env(
    "DJANGO_SECRET_KEY", default="1EJjhdOOqcnEU4ybJFEMo1jBpWmuv44YObROluFTEWc="
)
if "DJANGO_SECRET_KEY" in os.environ and PRODUCTION:
    django_secret_key = json.loads(get_secret(os.environ["DJANGO_SECRET_KEY"])["SecretString"])
    SECRET_KEY = django_secret_key["DJANGO_SECRET_KEY"]


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False if PRODUCTION else env.bool("DJANGO_DEBUG", default=True)

ALLOWED_HOSTS = [prod_required_env("DJANGO_ALLOWED_HOST", default="*")]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "backend",
    "willing_zg",
]

MIDDLEWARE = [
    "backend.proxy.ReverseProxyHandlingMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

if "DATABASE_SECRET" in os.environ:
    db_secret = json.loads(get_secret(os.environ["DATABASE_SECRET"])["SecretString"])

    db_username = db_secret["username"]
    db_password = db_secret["password"]
    db_host = db_secret["host"]
    db_port = str(db_secret["port"])
    db_clusterid = db_secret["dbClusterIdentifier"]

    db_url = f"postgres://{db_username}:{db_password}@{db_host}:{db_port}/{db_clusterid}"
    os.environ["DATABASE_URL"] = db_url


db_config = env.db_url("DATABASE_URL", default="postgres://postgres:postgres@db/postgres")
DATABASES = {"default": db_config}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"


# Cookies
SHARED_DOMAIN = prod_required_env("DJANGO_SHARED_DOMAIN", default=None)
CSRF_COOKIE_DOMAIN = SHARED_DOMAIN
CSRF_TRUSTED_ORIGINS = SHARED_DOMAIN and [f".{SHARED_DOMAIN}"]
SESSION_COOKIE_DOMAIN = SHARED_DOMAIN
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_AGE = 3600
CSRF_COOKIE_AGE = SESSION_COOKIE_AGE
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG


# Set security headers
X_FRAME_OPTIONS = "DENY"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True


REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": (
        "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
        "djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "djangorestframework_camel_case.parser.CamelCaseFormParser",
        "djangorestframework_camel_case.parser.CamelCaseMultiPartParser",
        "djangorestframework_camel_case.parser.CamelCaseJSONParser",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "simplejwt_extensions.authentication.JWTAuthentication",
    ),
}

# production must use SMTP. others will use DJANGO_EMAIL_BACKEND or default to "console"
EMAIL_BACKEND = "django.core.mail.backends.{}.EmailBackend".format(
    env.str("DJANGO_EMAIL_BACKEND", default="console") if DEBUG else "smtp"
)
EMAIL_HOST = "email-smtp.us-east-1.amazonaws.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = prod_required_env("DJANGO_EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = prod_required_env("DJANGO_EMAIL_HOST_PASSWORD", "")
if "DJANGO_EMAIL_HOST_PASSWORD" in os.environ:
    django_password = json.loads(
        get_secret(os.environ["DJANGO_EMAIL_HOST_PASSWORD"])["SecretString"]
    )
    EMAIL_HOST_PASSWORD = django_password["DJANGO_EMAIL_HOST_PASSWORD"]

EMAIL_USE_TLS = True

SUPPORT_PHONE_NUMBER = "+1 (855) 943-4177"
SUPPORT_EMAIL_ADDRESS = "clientservice@legalplans.com"
PANEL_EMAIL_ADDRESS = "panel@legalplans.com"

DEFAULT_VERIFYING_KEY = """MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC91RWCawEvxQj+tigRvuHxouO8
jKd35ukUxFBFRAGcI57firbAkFII6zPIiWAENGMqtjX57hk9EjAZ27XvQ4SQACvD
5j7htsJT31bZbVUH7a3JEDpxa02VXpXdfPYSs8umZkdxMxxmiD9uH9VmLN3VS14l
xQlyJdlvbLmNCAf6uwIDAQAB"""

NAKED_VERIFYING_KEY = prod_required_env("DJANGO_JWT_VERIFYING_KEY", DEFAULT_VERIFYING_KEY)

if "DJANGO_JWT_VERIFYING_KEY" in os.environ and PRODUCTION:
    NAKED_VERIFYING_KEY = json.loads(
        get_secret(os.environ["DJANGO_JWT_VERIFYING_KEY"])["SecretString"]
    )["DJANGO_JWT_VERIFYING_KEY"]


VERIFYING_KEY = f"""-----BEGIN PUBLIC KEY-----
{NAKED_VERIFYING_KEY.replace(" ", "")}
-----END PUBLIC KEY-----"""

SIMPLE_JWT = {
    "USER_ID_FIELD": "public_id",
    "ALGORITHM": "RS512",
    "SIGNING_KEY": None,
    "VERIFYING_KEY": VERIFYING_KEY,
}
