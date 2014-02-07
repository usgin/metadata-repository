## Prerequisites

- Node.js
- Coffeescript

    $ sudo npm install -g coffee-script

## Setup a Virtual Environment for the Metadata Repository

    $ virtualenv --no-site-packages metadatarepoenv
    $ cd ~/metadatarepoenv
    $ source bin/activate

## Setup the Metadata Repository

    (metadatarepoenv) $ git clone git@github.com:usgin/metadata-repository.git
    (metadatarepoenv) $ cd metadata-repository/
    (metadatarepoenv) $ pip install -r pip-requirements.txt

## Setup Django

- Create a new Django project called metadatarepo

    (metadatarepoenv) $ cd ..
    (metadatarepoenv) $ django-admin.py startproject metadatarepo

- Setup symlinks

    (metadatarepoenv) $ cd metadatarepo/
    (metadatarepoenv) $ ln -s ~/workspace/metadatarepoenv/metadata-repository/metadatadb ~/workspace/metadatarepoenv/metadatarepo
    (metadatarepoenv) $ ln -s ~/workspace/metadatarepoenv/metadata-repository/ui ~/workspace/metadatarepoenv/metadatarepo
    (metadatarepoenv) $ ln -s ~/workspace/metadatarepoenv/metadata-repository/registry ~/workspace/metadatarepoenv/metadatarepo

- Compile CoffeeScript into JavaScript

    (metadatarepoenv) $ cd ui/
    (metadatarepoenv) $ cake build

- Replace the content of metadatarepo/metadatarepo/urls.py with metadata-repository/dgn/urls.py


### Setup Postgres Databases

    (metadatarepoenv) $ sudo -su postgres
    $ createuser -s -d -r -P metadatarepouser
    $ createdb -T template_postgis -O metadatarepouser metadatarepo -E utf-8
    $ psql -d metadatarepo -c '\dt'
    $ psql -d metadatarepo -c 'ALTER TABLE geometry_columns OWNER TO metadatarepouser;'
    $ psql -d metadatarepo -c 'ALTER TABLE spatial_ref_sys OWNER TO metadatarepouser;'
    $ exit

### Edit settings.py

Open /metadatarepo/metadatarepo/settings.py in an editor and change the following settings (for Django v1.4):


    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psyc$
            'NAME': 'metadatarepo',          # Or path to database file if using$
            'USER': 'metadatarepouser',      # Not used with sqlite3.
            'PASSWORD': 'your password',     # Not used with sqlite3.
            'HOST': 'localhost',             # Set to empty string for localhost. Not $
            'PORT': '5432',                  # Set to empty string for default. Not us$
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
        'captcha'
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

### Sync Django with Postgres

    (metadatarepoenv) $ cd metadatarepo/
    (metadatarepoenv) $ python manage.py syncdb

GeoDjango v1.4 might have deployed with a buggy version of libgeos.  If it did, you won't be able to get past the above step without doing the following:

    $ sudo nano ../python2.7/site-packages/django/contrib/gis/geos/libgeos.py
    Change this:
    $ version_regex = re.compile(r'^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<subminor>\d+))((rc(?P<release_candidate>\d+))|dev)?-CAPI-(?P<capi_version>\d+\.\d+\.\d+)$')
    To this:
    $ version_regex = re.compile(r'^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<subminor>\d+))((rc(?P<release_candidate>\d+))|dev)?-CAPI-(?P<capi_version>\d+\.\d+\.\d+).*$')
