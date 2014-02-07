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
