**This repository contains four Django applications which rely on outdated APIs.  Users should install this software into a virtual environment and install all of the requirements in `pip-requirements.txt` to ensure that everything works properly**

[Here's some low level documentation on getting this software running in Ubuntu 12.04](https://github.com/usgin/metadata-repository/wiki/Low-Level-Installation-Documentation)

### Prerequisites
- Node.js
- Coffeescript
- Python virtualenv
- PostgreSQL w/ PostGIS
- [USGIN Metadata Server](https://github.com/usgin/metadata-server)

### Installation Notes
This repository contains four Django applications:
- dgn
- metadatadb
- registry
- ui

But the `dgn` application is not necessary.  Each application contains a `urls.py` file which follows the standard Django URL structure.  Unless you feel like changing the defined URL structures, the file structure of your virtual environment should look like this:

    ----my-virtual-environment|
        bin
        include
        lib
        metadata-repository
        metadata-server
    --------my-django-project|
            media
            metadatadb (symbolic link from ../metadata-repository)
            registry (symbolic link from ../metadata-repository)
            static
            ui (symbolic link from ../metadata-repository)
            my-django-project

Here are some example core Django files to help you finish up the installation process:
- [my-django-project/settings.py](https://github.com/usgin/metadata-repository/blob/master/django-example/settings-example.py)
- [my-django-project/urls.py](https://github.com/usgin/metadata-repository/blob/master/django-example/urls-example.py)


And to build *.js files, you'll need to:

    $ cd metadata-repository/ui
    $ cake build
