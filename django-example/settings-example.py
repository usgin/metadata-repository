# Django settings for usginmetadata project.

DEBUG = True
TEMPLATE_DEBUG = True

ADMINS = (
    ('Enter your username here', 'and your email address here'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'Enter the name of your django database here',
        'USER': 'and the name of your django user here',
        'PASSWORD': 'and that user\'s password here',
        'HOST': 'probably 127.0.0.1',
        'PORT': 'your postgres port'
    }
}

TIME_ZONE = 'your timezone'
LANGUAGE_CODE = 'your language'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True
MEDIA_ROOT = '/absolute/path/from/root/to/media/folder'
MEDIA_URL = '/media/'
STATIC_ROOT = '/absolute/path/from/root/to/static/folder'
STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
)

SECRET_KEY = 'generated auto-magically with two fingers by django'

TEMPLATE_LOADERS = (
    ('pyjade.ext.django.Loader',(
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "ui.context_processors.basics"
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'generated auto-magically with two fingers by django'

WSGI_APPLICATION = 'generated auto-magically with two fingers by django'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'metadatadb',
    'registry',
    'ui',
    'captcha',
)

RECAPTCHA_PUBLIC_KEY = 'go here -- https://www.google.com/recaptcha/admin/create'
RECAPTCHA_PRIVATE_KEY = 'go here -- https://www.google.com/recaptcha/admin/create'
EMAIL_HOST = 'merton.webserversystems.com'
EMAIL_PORT = 2525
EMAIL_HOST_USER = 'metadata@usgin.org'
EMAIL_HOST_PASSWORD = 'paEWNKQj'
EMAIL_USE_TLS = False
SERVER_EMAIL = EMAIL_HOST_USER
SITE_ID = 1
AUTH_PROFILE_MODULE = 'ui.UserProfile'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
