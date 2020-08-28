from datetime import timedelta

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .zygoat_settings import *  # noqa

AUTH_USER_MODEL = "authentication.User"

INSTALLED_APPS = [
    *INSTALLED_APPS,
    "authentication",
    "rest_framework_simplejwt.token_blacklist",
    "axes",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    *MIDDLEWARE,
    "axes.middleware.AxesMiddleware",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "simplejwt_extensions.authentication.JWTAuthentication",
    ),
}

AUTHENTICATION_BACKENDS = [
    # AxesBackend should be the first backend in the AUTHENTICATION_BACKENDS list.
    "axes.backends.AxesBackend",
    "django.contrib.auth.backends.ModelBackend",
]

AXES_FAILURE_LIMIT = env.int("DJANGO_AXES_FAILURE_LIMIT", default=5)
AXES_USERNAME_FORM_FIELD = "email"
AXES_RESET_ON_SUCCESS = True
AXES_ONLY_USER_FAILURES = True
AXES_USERNAME_CALLABLE = "authentication.utils.get_username"
AXES_LOCKOUT_CALLABLE = "authentication.utils.generate_axes_lockout_response"

DEFAULT_SIGNING_KEY = """MIICXQIBAAKBgQC91RWCawEvxQj+tigRvuHxouO8jKd35ukUxFBFRAGcI57firbA
kFII6zPIiWAENGMqtjX57hk9EjAZ27XvQ4SQACvD5j7htsJT31bZbVUH7a3JEDpx
a02VXpXdfPYSs8umZkdxMxxmiD9uH9VmLN3VS14lxQlyJdlvbLmNCAf6uwIDAQAB
AoGACXFcDIy+Fl46wFDXVWqlWpu7sFleyzwVRA8v3wIvAlFTSdNgm9uR+ReaD9Ol
jw/8DtfZf4E0iDEra13egvRc16byYQ4qv0l7xvn3ATomxcPwbdvkfYE4C0EZFuXx
ZZwSQwWsNl/36BSyZErw8y/THMIkOKRNFuJarK4P3aYppEECQQDpvRnL2kbbXbqW
uB8Pt2hMfBXW/byCcctoI+cuqYAUJ/J1tLPe+q7sAW6Fr0WpYTpjljC+UCqu/a6a
YgG0L6I5AkEAz+l7QfyFKk7jl05hEUly0CNshgJ8jLPcF2ZXILrcUwGxbpdyjmCJ
ExiKpfzPufYeu7qLwhyaHniR9huSZIx0kwJBALMRTFIAR4iHpgsRw7omqKDv70tl
2KWWyF5gIxx8fsLyV64VYjfRlXD5J9MDFDtPYYwp4+3pPMoTT1C3BNcmJwECQEYV
Ero0b4LKYsce4XNdSblFJ5Coh+k5u2eb1KSwuBG20WNQ44mAmtP4AsxewnqRrtxi
zjdZQs4goDrQInGIMscCQQCIT5jvRb197iRinBqpNy01i7GdlLtMC7Z9V/PV0YW1
GmX50gvd7aA+i2UuZj7BxapFStyEGl4Nggglnn+QqQ+L"""

NAKED_SIGNING_KEY = prod_required_env("DJANGO_JWT_SIGNING_KEY", DEFAULT_SIGNING_KEY)

if "DJANGO_JWT_SIGNING_KEY" in os.environ and PRODUCTION:
    NAKED_SIGNING_KEY = json.loads(
        get_secret(os.environ["DJANGO_JWT_SIGNING_KEY"])["SecretString"]
    )["DJANGO_JWT_SIGNING_KEY"]
SIGNING_KEY = f"""-----BEGIN RSA PRIVATE KEY-----
{NAKED_SIGNING_KEY.replace(" ", "")}
-----END RSA PRIVATE KEY-----"""

# Override the values set by willing-zg simple jwt plugin
SIMPLE_JWT["USER_ID_FIELD"] = "portunus_uuid"
SIMPLE_JWT["SIGNING_KEY"] = SIGNING_KEY
SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"] = timedelta(hours=1)

CORS_ORIGIN_ALLOW_ALL = DEBUG
CORS_ALLOW_CREDENTIALS = True
if not DEBUG:
    CORS_ORIGIN_REGEX_WHITELIST = [
        r"^https://[\w.]+\.willing\.com$",
        r"^https://[\w.]+\.legalplans\.com$",
    ]

BASE_URL = env("DJANGO_BASE_URL", default="http://localhost:3001/")

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 7,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "authentication.password_validators.AlphaNumericPasswordValidator",
    },
]

DEFAULT_REDIRECT_URL = prod_required_env(
    "DJANGO_DEFAULT_REDIRECT_URL", "http://localhost:3001"
)
VALID_REDIRECT_HOSTNAMES = ["*.willing.com", "*.legalplans.com"]

if not PRODUCTION:
    VALID_REDIRECT_HOSTNAMES.append("localhost")

SESSION_COOKIE_SAMESITE = None

# Sentry
SENTRY_DSN = prod_required_env("DJANGO_SENTRY_DSN", default=None)
ENVIRONMENT = prod_required_env("DJANGO_ENVIRONMENT", default=None)

if SENTRY_DSN is not None:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        send_default_pii=True,
        environment=ENVIRONMENT,
    )

ZYGOAT_FRONTEND_META_CONFIG = {
    "sentry_dsn": prod_required_env(
        "DJANGO_FRONTEND_SENTRY_DSN",
        default="https://8db6b816b01548e0bacdb9bdbeb2caf8@o39628.ingest.sentry.io/5339664",
    ),
    "sentry_environment": ENVIRONMENT,
}
