# ruff: noqa: E501
from .base import *  # noqa: F403
from .base import DATABASES
from .base import INSTALLED_APPS
{%- if cookiecutter.use_drf == "y" %}
from .base import SPECTACULAR_SETTINGS
{%- endif %}
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env("DJANGO_SECRET_KEY")
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["{{ cookiecutter.domain_name }}"])

# DATABASES
# ------------------------------------------------------------------------------
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)

# CACHES
# ------------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # Mimicing memcache behavior.
            # https://github.com/jazzband/django-redis#memcached-exceptions-behavior
            "IGNORE_EXCEPTIONS": True,
        },
    },
}

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-ssl-redirect
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-secure
SESSION_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-name
SESSION_COOKIE_NAME = "__Secure-sessionid"
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-secure
CSRF_COOKIE_SECURE = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-name
CSRF_COOKIE_NAME = "__Secure-csrftoken"
# https://docs.djangoproject.com/en/dev/topics/security/#ssl-https
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-seconds
# TODO: set this to 60 seconds first and then to 518400 once you prove the former works
SECURE_HSTS_SECONDS = 60
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-include-subdomains
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS",
    default=True,
)
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-preload
SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=True)
# https://docs.djangoproject.com/en/dev/ref/middleware/#x-content-type-options-nosniff
SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
    "DJANGO_SECURE_CONTENT_TYPE_NOSNIFF",
    default=True,
)

{% if cookiecutter.cloud_provider != 'None' -%}
# STORAGES
# ------------------------------------------------------------------------------
# https://django-storages.readthedocs.io/en/latest/#installation
INSTALLED_APPS += ["storages"]
{%- endif -%}
{% if cookiecutter.cloud_provider == 'AWS' %}
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_ACCESS_KEY_ID = env("DJANGO_AWS_ACCESS_KEY_ID")
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_SECRET_ACCESS_KEY = env("DJANGO_AWS_SECRET_ACCESS_KEY")
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_STORAGE_BUCKET_NAME = env("DJANGO_AWS_STORAGE_BUCKET_NAME")
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_QUERYSTRING_AUTH = False
# DO NOT change these unless you know what you're doing.
_AWS_EXPIRY = 60 * 60 * 24 * 7
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": f"max-age={_AWS_EXPIRY}, s-maxage={_AWS_EXPIRY}, must-revalidate",
}
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_S3_MAX_MEMORY_SIZE = env.int(
    "DJANGO_AWS_S3_MAX_MEMORY_SIZE",
    default=100_000_000,  # 100MB
)
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#settings
AWS_S3_REGION_NAME = env("DJANGO_AWS_S3_REGION_NAME", default=None)
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#cloudfront
AWS_S3_CUSTOM_DOMAIN = env("DJANGO_AWS_S3_CUSTOM_DOMAIN", default=None)
aws_s3_domain = AWS_S3_CUSTOM_DOMAIN or f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
{% elif cookiecutter.cloud_provider == 'GCP' %}
GS_BUCKET_NAME = env("DJANGO_GCP_STORAGE_BUCKET_NAME")
GS_DEFAULT_ACL = "publicRead"
{% elif cookiecutter.cloud_provider == 'Azure' %}
AZURE_ACCOUNT_KEY = env("DJANGO_AZURE_ACCOUNT_KEY")
AZURE_ACCOUNT_NAME = env("DJANGO_AZURE_ACCOUNT_NAME")
AZURE_CONTAINER = env("DJANGO_AZURE_CONTAINER_NAME")
{% endif -%}

{% if cookiecutter.cloud_provider != 'None' or cookiecutter.use_whitenoise == 'y' -%}
# STATIC & MEDIA
# ------------------------
STORAGES = {
{%- if cookiecutter.use_whitenoise == 'y' and cookiecutter.cloud_provider == 'None' %}
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
{%- elif cookiecutter.cloud_provider == 'AWS' %}
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "location": "media",
            "file_overwrite": False,
        },
    },
    {%- if cookiecutter.use_whitenoise == 'y' %}
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    {%- else %}
    "staticfiles": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "location": "static",
            "default_acl": "public-read",
        },
    },
    {%- endif %}
{%- elif cookiecutter.cloud_provider == 'GCP' %}
    "default": {
        "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
        "OPTIONS": {
            "location": "media",
            "file_overwrite": False,
        },
    },
    {%- if cookiecutter.use_whitenoise == 'y' %}
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    {%- else %}
    "staticfiles": {
        "BACKEND": "storages.backends.gcloud.GoogleCloudStorage",
        "OPTIONS": {
            "location": "static",
            "default_acl": "publicRead",
        },
    },
    {%- endif %}
{%- elif cookiecutter.cloud_provider == 'Azure' %}
    "default": {
        "BACKEND": "storages.backends.azure_storage.AzureStorage",
        "OPTIONS": {
            "location": "media",
            "file_overwrite": False,
        },
    },
    {%- if cookiecutter.use_whitenoise == 'y' %}
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    {%- else %}
    "staticfiles": {
        "BACKEND": "storages.backends.azure_storage.AzureStorage",
        "OPTIONS": {
            "location": "static",
        },
    },
    {%- endif %}
{%- endif %}
}
{%- endif %}

{%- if cookiecutter.cloud_provider == 'AWS' %}
MEDIA_URL = f"https://{aws_s3_domain}/media/"
{%- if cookiecutter.use_whitenoise == 'n' %}
COLLECTFAST_STRATEGY = "collectfast.strategies.boto3.Boto3Strategy"
STATIC_URL = f"https://{aws_s3_domain}/static/"
{%- endif %}
{%- elif cookiecutter.cloud_provider == 'GCP' %}
MEDIA_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/media/"
{%- if cookiecutter.use_whitenoise == 'n' %}
COLLECTFAST_STRATEGY = "collectfast.strategies.gcloud.GoogleCloudStrategy"
STATIC_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/static/"
{%- endif %}
{%- elif cookiecutter.cloud_provider == 'Azure' %}
MEDIA_URL = f"https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net/media/"
{%- if cookiecutter.use_whitenoise == 'n' %}
STATIC_URL = f"https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net/static/"
{%- endif %}
{%- endif %}

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#default-from-email
DEFAULT_FROM_EMAIL = env(
    "DJANGO_DEFAULT_FROM_EMAIL",
    default="{{cookiecutter.project_name}} <noreply@{{cookiecutter.domain_name}}>",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = env("DJANGO_SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)
# https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
EMAIL_SUBJECT_PREFIX = env(
    "DJANGO_EMAIL_SUBJECT_PREFIX",
    default="[{{cookiecutter.project_name}}] ",
)

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL regex.
ADMIN_URL = env("DJANGO_ADMIN_URL")

# Anymail
# ------------------------------------------------------------------------------
# https://anymail.readthedocs.io/en/stable/installation/#installing-anymail
INSTALLED_APPS += ["anymail"]
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
# https://anymail.readthedocs.io/en/stable/installation/#anymail-settings-reference
{%- if cookiecutter.mail_service == 'Amazon SES' %}
# https://anymail.readthedocs.io/en/stable/esps/amazon_ses/
EMAIL_BACKEND = "anymail.backends.amazon_ses.EmailBackend"
ANYMAIL = {}
{%- elif cookiecutter.mail_service == 'Sendgrid' %}
# https://anymail.readthedocs.io/en/stable/esps/sendgrid/
EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"
ANYMAIL = {
    "SENDGRID_API_KEY": env("SENDGRID_API_KEY"),
    "SENDGRID_API_URL": env("SENDGRID_API_URL", default="https://api.sendgrid.com/v3/"),
}
{%- elif cookiecutter.mail_service == 'Other SMTP' %}
# https://anymail.readthedocs.io/en/stable/esps
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
ANYMAIL = {}
{%- endif %}

# django-compressor
# ------------------------------------------------------------------------------
# https://django-compressor.readthedocs.io/en/latest/settings/#django.conf.settings.COMPRESS_ENABLED
COMPRESS_ENABLED = env.bool("COMPRESS_ENABLED", default=True)
{%- if cookiecutter.cloud_provider == 'None' %}
# https://django-compressor.readthedocs.io/en/latest/settings/#django.conf.settings.COMPRESS_STORAGE
COMPRESS_STORAGE = "compressor.storage.GzipCompressorFileStorage"
{%- elif cookiecutter.cloud_provider in ('AWS', 'GCP', 'Azure') and cookiecutter.use_whitenoise == 'n' %}
# https://django-compressor.readthedocs.io/en/latest/settings/#django.conf.settings.COMPRESS_STORAGE
COMPRESS_STORAGE = STORAGES["staticfiles"]["BACKEND"]
{%- endif %}
# https://django-compressor.readthedocs.io/en/latest/settings/#django.conf.settings.COMPRESS_URL
COMPRESS_URL = STATIC_URL{% if cookiecutter.use_whitenoise == 'y' or cookiecutter.cloud_provider == 'None' %}  # noqa: F405
{%- endif -%}
{%- if cookiecutter.use_whitenoise == 'y' %}
# https://django-compressor.readthedocs.io/en/latest/settings/#django.conf.settings.COMPRESS_OFFLINE
COMPRESS_OFFLINE = True  # Offline compression is required when using Whitenoise
{%- endif %}
# https://django-compressor.readthedocs.io/en/latest/settings/#django.conf.settings.COMPRESS_FILTERS
COMPRESS_FILTERS = {
    "css": [
        "compressor.filters.css_default.CssAbsoluteFilter",
        "compressor.filters.cssmin.rCSSMinFilter",
    ],
    "js": ["compressor.filters.jsmin.JSMinFilter"],
}
{%- if cookiecutter.use_whitenoise == 'n' -%}
# Collectfast
# ------------------------------------------------------------------------------
# https://github.com/antonagestam/collectfast#installation
INSTALLED_APPS = ["collectfast", *INSTALLED_APPS]
{% endif %}
# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
{% if cookiecutter.use_drf == "y" -%}

# django-rest-framework
# -------------------------------------------------------------------------------
# Tools that generate code samples can use SERVERS to point to the correct domain
SPECTACULAR_SETTINGS["SERVERS"] = [
    {"url": "https://{{ cookiecutter.domain_name }}", "description": "Production server"},
]

{%- endif %}
# Your stuff...
# ------------------------------------------------------------------------------
