# Installation of DGN in VirtualBox
- Starting ISO: [Ubuntu 12.04 x64](http://www.ubuntu.com/download/desktop)
- Usernames / Passwords:
	
	Unix user: dgn
	password: secret
	
	Unix user: postgres
	password: secret
	
	Postgres user: dgn
	password: secret
	
	Postgres user: gpt
	password: secret
	
	Geoportal user: gptadmin
	password: secret
	
	
	
	
## Install Updates, VirtualBox Guest Additions and Additional Drivers
... then restart

## Package Installations

	sudo apt-get install python-dev make gcc build-essential libpq-dev postgresql postgresql-contrib postgresql-server-dev-9.1 libxml2-dev libxslt-dev binutils unzip git subversion python-software-properties tomcat7 tomcat7-admin ant openjdk-7-jdk
	
## Python Preparations

	cd ~/Downloads
	wget http://pypi.python.org/packages/2.7/s/setuptools/setuptools-0.6c11-py2.7.egg
	sudo sh setuptools-0.6c11-py2.7.egg
	sudo easy_install psycopg2
	sudo easy_install lxml
	sudo easy_install beautifulsoup4
	sudo easy_install pyjade
	
## Install Geospatial Libraries
### Download

	wget http://download.osgeo.org/geos/geos-3.3.3.tar.bz2
	wget http://download.osgeo.org/proj/proj-4.8.0.tar.gz
	wget http://download.osgeo.org/proj/proj-datumgrid-1.5.zip
	wget http://download.osgeo.org/gdal/gdal-1.9.1.tar.gz
	wget http://postgis.refractions.net/download/postgis-1.5.3.tar.gz
	wget http://downloads.esri.com/Support/downloads/ao_/FileGDB_API_1_2-64.tar.gz
	
### Install GEOS

	tar xjf geos-3.3.3.tar.bz2
	cd geos-3.3.3
	./configure
	make
	sudo make install
	sudo ldconfig
	
### Install Proj

	cd ~/Downloads
	tar xzf proj-4.8.0.tar.gz
	cd proj-4.8.0/nad
	unzip ../../proj-datumgrid-1.5.zip
	cd ..
	./configure
	make
	sudo make install
	sudo ldconfig
	
### Install GDAL

	cd ~/Downloads
	tar xzf FileGDB_API_1_2-64.tar.gz 
	cd ~/Downloads/FileGDB_API/lib
	ln -s libfgdbunixrtl.so libfgdblinuxrtl.so
	sudo sh -c 'echo "/home/ubuntu/downloads/FileGDB_API/lib" >> /etc/ld.so.conf'
	sudo ldconfig
	cd ../..
	tar xvf gdal-1.9.1.tar.gz
	cd gdal-1.9.1
	./configure --with-pg=/usr/bin/pg_config --with-fgdb=/home/ubuntu/downloads/FileGDB_API --with-geos=/usr/local/bin/geos-config --with-static-proj4=/usr/local/lib/libproj.a --with-python
	make
	sudo make install
	sudo ldconfig
	
### Install PostGIS

	cd ~/Downloads
	tar xzf postgis-1.5.3.tar.gz
	cd postgis-1.5.3
	./configure
	make
	sudo make install

## Create and Configure a PostGIS Database
### Create a PostGIS Template Database

	cd ~/Downloads
	wget https://docs.djangoproject.com/en/dev/_downloads/create_template_postgis-debian.sh
	chmod 755 create_template_postgis-debian.sh
	sudo passwd postgres
	su postgres
	./create_template_postgis-debian.sh
	exit
	
### Create a PostgreSQL user for the Django to use

	su postgres
	createuser --createdb --pwprompt dgn
	exit
	
### Configure PostgreSQL to allow password authentication for Django

	sudo sed -i 's/# "local" is for Unix domain socket connections only/local  all  all    password/' /etc/postgresql/9.1/main/pg_hba.conf
	sudo /etc/init.d/postgresql restart
	
### Finally, create a PostGIS-enabled database for Django to use

	psql --username=dgn --password --dbname=postgres --command="CREATE DATABASE dgn TEMPLATE template_postgis;"
	
## Install Django

	cd ~/Downloads
	git clone git://github.com/django/django.git
	sudo sh -c "echo '/home/dgn/downloads/django' > /usr/lib/python2.7/dist-packages/django.pth"
	sudo ln -s /home/dgn/downloads/django/django/bin/django-admin.py /usr/local/bin
	
## Install Geoserver

	cd ~/Downloads
	wget http://downloads.sourceforge.net/geoserver/geoserver-2.1.4-war.zip
	mkdir geoserver-2.1.4
	cd geoserver-2.1.4
	unzip ../geoserver-2.1.4-war.zip
	sudo cp geoserver.war /var/lib/tomcat7/webapps/
	
## Install Geoportal
### Checkout Geoportal source code and USGIN add-on

	cd ~/Downloads
	svn co https://geoportal.svn.sourceforge.net/svnroot/geoportal/Geoportal/trunk geoportal
	cd geoportal
	git clone git://github.com/usgin/usgin-geoportal-addon.git usgin
	
### Configure Ant

	sudo ln-s /usr/share/tomcat7/lib/catalina-ant.jar /usr/share/ant/lib
	
### Create a PostgreSQL user for Geoportal to use

	su postgres
	createuser --createdb --pwprompt gpt
	exit
	
### Create a PostgreSQL database for Geoportal to use

	psql --username=gpt --password --dbname=postgres --command="CREATE DATABASE gpt;"
	psql --username=gpt --password --dbname=gpt --file=etc/sql/schema_pg.sql

### Configure Geoportal Add-on

	cp usgin/build/local.properties-example usgin/build/local.properties
	mkdir ~/geoportal
	mkdir ~/geoportal/lucene
	mkdir ~/geoportal/lucene/index
	mkdir ~/geoportal/lucene/ratings
	sudo chown -R tomcat7:tomcat7 ~/geoportal
	sed -i 's/local.tomcat.home=\/usr\/share\/tomcat6/local.tomcat.home=\/usr\/share\/tomcat7/' usgin/build/local.properties
	sed -i 's/local.lucene.index.location=\/home\/user\/geoportal\/lucene\/index/local.lucene.index.location=\/home\/dgn\/geoportal\/lucene\/index/' usgin/build/local.properties	
	sed -i 's/local.lucene.rating.location=\/home\/user\/geoportal\/lucene\/ratings/local.lucene.index.location=\/home\/dgn\/geoportal\/lucene\/ratings/' usgin/build/local.properties
	sed -i 's/local.db.user.name=user/local.db.user.name=gpt/' usgin/build/local.properties
	sed -i 's/local.admin.name=adminuser/local.admin.name=gptadmin/' usgin/build/local.properties
	cd ~/Downloads
	wget http://jdbc.postgresql.org/download/postgresql-9.1-902.jdbc4.jar
	cp postgresql-9.1-902.jdbc4.jar geoportal/usgin/build/lib/
	
### Install Geoportal

	cd ~/Downloads/geoportal/usgin/build
	sudo update-alternatives --config java # choose the openjdk-7 option
	ant war
	cd ~/Downloads/geoportal/build
	cp geoportal.war /var/lib/tomcat7/webapps/