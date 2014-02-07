## Setup a Virtual Environment for the Metadata Repository

    $ virtualenv --no-site-packages metadatarepoenv
    $ cd ~/metadatarepoenv
    $ source bin/activate

## Setup the Metadata Repository

    (metadatarepoenv) $ git clone git@github.com:usgin/metadata-repository.git
    (metadatarepoenv) $ cd /metadata-repository
    (metadatarepoenv) $ pip install -r pip-requirements.txt

## Setup Django

    (metadatarepoenv) $ cd ..
    (metadatarepoenv) $ django-admin.py startproject metadatarepo

### Setup Postgres Databases

    (metadatarepoenv) $ sudo -su postgres
    $ createuser -S -D -R -P metadatarepouser
    $ createdb -T template_postgis -O metadatarepouser metadatarepo -E utf-8
    $ psql -d metadatarepo -c '\dt'
    $ psql -d metadatarepo -c 'ALTER TABLE geometry_columns OWNER TO metadatarepouser;'
    $ psql -d metadatarepo -c 'ALTER TABLE spatial_ref_sys OWNER TO metadatarepouser;'
    $ exit

### Setup settings.py

Open /metadatarepo/metadatarepo/settings.py is an editor and change the following settings:


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psyc$
        'NAME': 'metadatarepo',                      # Or path to database file if using$
        'USER': 'metadatarepouser',                      # Not used with sqlite3.
        'PASSWORD': 'your password',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not $
        'PORT': '',                      # Set to empty string for default. Not us$
    }
}

TIME_ZONE = 'America/Phoenix'


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
    'uriredirect',
    'modelmanager'
)

RECAPTCHA_PUBLIC_KEY = '6Lf-1tQSAAAAAPNBFjd5S6GJta2X7YlFiA-FEnCp'
RECAPTCHA_PRIVATE_KEY = '6Lf-1tQSAAAAACvEUyJ2wBKKueBO5_GQ-ilxtfiM'
EMAIL_HOST = 'mail.azgs.az.gov'
EMAIL_PORT = 2525
EMAIL_HOST_USER = 'web-admin@azgs.az.gov'
EMAIL_HOST_PASSWORD = 'paEWNKQj'
EMAIL_USE_TLS = False
SERVER_EMAIL = EMAIL_HOST_USER
SITE_ID = 1
AUTH_PROFILE_MODULE = 'ui.UserProfile'


## Required settings defined in settings.py
	RECAPTCHA_PUBLIC_KEY
	RECAPTCHA_PRIVATE_KEY
	EMAIL_HOST
	EMAIL_PORT
	EMAIL_HOST_USER
	EMAIL_HOST_PASSWORD
	EMAIL_USE_TLS
	SERVER_EMAIL
	SITE_ID
