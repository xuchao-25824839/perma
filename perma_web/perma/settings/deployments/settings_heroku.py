# this file will be moved by heroku-buildpack-perma to ../settings.py
from .deployments.settings_prod import *

# ###########
# # ROLLBAR #
# ###########
#
# # Backend
# MIDDLEWARE_CLASSES += ('rollbar.contrib.django.middleware.RollbarNotifierMiddleware',)
# ROLLBAR = {
#     'access_token': os.environ.get('ROLLBAR_ACCESS_TOKEN'),
#     'environment': 'development' if DEBUG else 'production',
#     'branch': os.environ.get('GIT_BRANCH'),
#     'root': '/app',
# }
#
# # Frontend
# ROLLBAR_CLIENT_ACCESS_TOKEN = os.environ.get('ROLLBAR_CLIENT_ACCESS_TOKEN')
# TEMPLATE_VISIBLE_SETTINGS += ('ROLLBAR_CLIENT_ACCESS_TOKEN',)
#
# # Logging - enables celery error reporting
# LOGGING['handlers']['rollbar'] = {
#     'level': 'ERROR',
#     'filters': ['require_debug_false'],
#     'access_token': os.environ.get('ROLLBAR_ACCESS_TOKEN'),
#     'environment': 'development' if DEBUG else 'production',
#     'class': 'rollbar.logger.RollbarHandler'
# }
# LOGGING['loggers']['']['handlers'] += ['rollbar']

# Parse database configuration from env
import dj_database_url
if os.environ.get('DEFAULT_DATABASE_URL', False):
    DATABASES['default'] = dj_database_url.config('DEFAULT_DATABASE_URL')
if os.environ.get('CDXLINE_DATABASE_URL', False):
    DATABASES['perma-cdxline'] = dj_database_url.config('CDXLINE_DATABASE_URL')
if os.environ.get('USE_RDS_CERT', False):
    DATABASES['default']['OPTIONS'] = DATABASES['perma-cdxline']['OPTIONS'] = {'ssl': {'ca': os.path.join(PROJECT_ROOT, 'amazon-rds-combined-ca-bundle.pem')}}

# Allow all host headers
# TODO: this is from Heroku's getting started with Django page -- is there a safer way?
ALLOWED_HOSTS = ['*']

DEFAULT_FILE_STORAGE = 'perma.storage_backends.S3MediaStorage'

# message passing
# settings via https://www.cloudamqp.com/docs/celery.html
CELERY_BROKER_POOL_LIMIT=1
CELERY_BROKER_URL = os.environ.get('CLOUDAMQP_URL')
CELERY_BROKER_CONNECTION_TIMEOUT = 30
CELERY_BROKER_HEARTBEAT = 30
CELERY_WORKER_SEND_TASK_EVENTS = False  # on the free CloudAMQP plan, celery events rapidly eat up our monthly message quota
CELERY_RESULT_BACKEND = os.environ.get('REDISCLOUD_URL')
CELERY_WORKER_HIJACK_ROOT_LOGGER = False

# logging
LOGGING['handlers']['default'] = {
    'level': 'INFO',
    'class': 'logging.StreamHandler',
    'formatter': 'standard',
}

ADMINS = (
    (os.environ.get('ADMIN_NAME', 'Your Name'), os.environ.get('ADMIN_EMAIL', 'your_email@example.com')),
)

# these are relative to the S3 bucket
MEDIA_ROOT = '/generated/'

# AWS storage settings
AWS_QUERYSTRING_AUTH = False

# archive creation
PHANTOMJS_LOG = 'phantomjs.log' # this will just get thrown away

# caching
CACHES['default']['LOCATION'] = os.environ.get('REDISCLOUD_URL')

# # thumbnail redis server
# THUMBNAIL_REDIS_DB = _parsed_redis_url['db']
# THUMBNAIL_REDIS_PASSWORD = _parsed_redis_url['password']
# THUMBNAIL_REDIS_HOST = _parsed_redis_url['host']
# THUMBNAIL_REDIS_PORT = _parsed_redis_url['port']


### OVERRIDE THESE WITH ENV VARS ###

# The host we want to display (used when DEBUG=False)
HOST = 'perma.cc'

# Amazon storage
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_STORAGE_BUCKET_NAME = ''
MEDIA_URL = 'http://BUCKET_NAME.s3.amazonaws.com/media/'


########## EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/1.3/ref/settings/#email-backend
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# See: https://docs.djangoproject.com/en/1.3/ref/settings/#email-host
# EMAIL_HOST = environ.get('EMAIL_HOST', 'smtp.gmail.com')

# See: https://docs.djangoproject.com/en/1.3/ref/settings/#email-host-password
# EMAIL_HOST_PASSWORD = environ.get('EMAIL_HOST_PASSWORD', '')

# See: https://docs.djangoproject.com/en/1.3/ref/settings/#email-host-user
# EMAIL_HOST_USER = environ.get('EMAIL_HOST_USER', 'your_email@example.com')

# See: https://docs.djangoproject.com/en/1.3/ref/settings/#email-port
# EMAIL_PORT = environ.get('EMAIL_PORT', 587)

# See: https://docs.djangoproject.com/en/1.3/ref/settings/#email-subject-prefix
# EMAIL_SUBJECT_PREFIX = '[%s] ' % SITE_NAME

# See: https://docs.djangoproject.com/en/1.3/ref/settings/#email-use-tls
# EMAIL_USE_TLS = True

# See: https://docs.djangoproject.com/en/1.3/ref/settings/#server-email
# SERVER_EMAIL = EMAIL_HOST_USER
########## END EMAIL CONFIGURATION
