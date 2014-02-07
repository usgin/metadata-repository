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

### Sync Django with Postgres

    (metadatarepoenv) $ python manage.py syncdb

GeoDjango v1.4 might have deployed with a buggy version of libgeos.  If it did, you won't be able to get past the above step without doing the following:

    $ sudo nano ../python2.7/site-packages/django/contrib/gis/geos/libgeos.py
    Change this:
    $ version_regex = re.compile(r'^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<subminor>\d+))((rc(?P<release_candidate>\d+))|dev)?-CAPI-(?P<capi_version>\d+\.\d+\.\d+)$')
    To this:
    $ version_regex = re.compile(r'^(?P<version>(?P<major>\d+)\.(?P<minor>\d+)\.(?P<subminor>\d+))((rc(?P<release_candidate>\d+))|dev)?-CAPI-(?P<capi_version>\d+\.\d+\.\d+).*$')

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
