# coding: utf-8
# Django settings for ninan project.

from os.path import join, abspath, dirname

here = lambda *x: join(abspath(dirname(__file__)), *x)
PROJECT_ROOT = here("..", "..")
root = lambda *x: join(abspath(PROJECT_ROOT), *x)

ADMINS = (('NinanAdmin', 'no-reply@ninan.com'), )

MANAGERS = ADMINS

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['ninan.sinaapp.com', 'localhost',
                 'www.ninan.sinaapp.com',
                 '1.ninan.sinaapp.com',
                 'ninan.vipsinaapp.com',
                 '127.0.0.1']

INTERNAL_IPS = ('127.0.0.1',)
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'zh-cn'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = root('static/upload')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/upload/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = root('static')

STATIC_URL = '/static/'
# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    root('ninan/static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '%qia1@8a)g(h#3nnnnnnnnnnnnnnnnnnnn'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
    'django.core.context_processors.request',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'ninan.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'ninan.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or
    # "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    root('templates'),
)

LOCALE_PATHS = (
    root('locale'),
)


FIXTURE_DIRS = (
    root('fixture'),
)

LANGUAGES = (
    ('en', 'English'),
    ('zh-cn', u'中文'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.sitemaps',
    'django.contrib.flatpages',
    'social.apps.django_app.default',
    'note',
    'reminder',
    'weixin',
    'south',
    'provider',
    'provider.oauth2',
    'tastypie',
    'milestone',
    'backends',
    'endless_pagination',
    'xlink',
    'feedfish',
    'handschopping',
    'haystack',
)

DATETIME_FORMAT = 'Y-m-d H:i:s'

# POP3 config
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = '25'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
SERVER_EMAIL = DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


DEFAULT_FILE_STORAGE = 'sae.ext.django.storage.backend.Storage'

STORAGE_BUCKET_NAME = ''

AMD_ROOT = 'sheffield'

EXPRESS_ID = ''
EXPRESS_KEY = ''

CACHE_USED_BY_DEBUG = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

CACHE_USED_BY_SAE = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': '127.0.0.1:11211'
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

WEIXIN_TOKEN = ''
WEIXIN_EMAIL = ''
WEIXIN_PASSWORD = ''
WEIXIN_ID = ''
WEIXIN_DEFAULT_COVER = 'uploads/cover.jpg'
WEIXIN_DEFAULT_COVER_ID = '201600537'

# ------------------ Cache Time ---------------------------------------
NOTE_VIEW_CACHE_TIME = 86400
WEIXIN_CACHE_TIME = 86400
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True

# ------------------- Social ------------------------------------------
AUTHENTICATION_BACKENDS = (
    'social.backends.weibo.WeiboOAuth2',
    'social.backends.douban.DoubanOAuth2',
    'social.backends.email.EmailAuth',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/done/'
URL_PATH = ''
SOCIAL_AUTH_STRATEGY = 'social.strategies.django_strategy.DjangoStrategy'
SOCIAL_AUTH_STORAGE = 'social.apps.django_app.default.models.DjangoStorage'
SOCIAL_AUTH_GOOGLE_OAUTH_SCOPE = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/userinfo.profile'
]
# SOCIAL_AUTH_EMAIL_FORM_URL = '/signup-email'
SOCIAL_AUTH_EMAIL_FORM_HTML = 'email_signup.html'
SOCIAL_AUTH_EMAIL_VALIDATION_FUNCTION = 'ninan.mail.send_validation'
SOCIAL_AUTH_EMAIL_VALIDATION_URL = '/email-sent/'
# SOCIAL_AUTH_USERNAME_FORM_URL = '/signup-username'
SOCIAL_AUTH_USERNAME_FORM_HTML = 'username_signup.html'

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'ninan.pipeline.require_email',
    'social.pipeline.mail.mail_validation',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details'
)

SOCIAL_AUTH_WEIBO_KEY = ''
SOCIAL_AUTH_WEIBO_SECRET = ''
SOCIAL_AUTH_DOUBAN_OAUTH2_KEY = ''
SOCIAL_AUTH_DOUBAN_OAUTH2_SECRET = ''

RESTRUCTUREDTEXT_FILTER_SETTINGS = {
    'initial_header_level': '3',
}

ENDLESS_PAGINATION_PER_PAGE = 4
ENDLESS_PAGINATION_LOADING = '<img src="/static/img/loader.gif" \
    alt="loading" />'

# Used by jieba
SAE_STORAGE_BUCKET_NAME = ''

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'utils.whoosh.whoosh_cn_backend.WhooshEngine',
        'PATH': 'whoosh',
        'STORAGE': 'file',
    },
}
