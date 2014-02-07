## Setup a Virtual Environment for the Metadata Repository

    $ virtualenv --no-site-packages metadatarepo
    $ cd ~/metadatarepo
    $ source bin/activate

## Setup the Metadata Repository

    (ckanenv) $ git clone git@github.com:usgin/metadata-repository.git
    (ckanenv) $ cd /metadata-repository
    (ckanenv) $ pip install -r pip-requirements.txt

## Setup Django

    (ckanenv) $ cd ..
    (ckanenv) $ django-admin.py startproject metadatarepo

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
