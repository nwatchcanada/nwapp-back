# HOWTO: Setup Over Fifty Five on MacOS for Development
## Description
The goal of this article is to provide step-by-step instructions on how to setup [nwapp-back](https://github.com/nwatchcanada/nwapp-back) on your ``MacOS`` local machine.

## Instructions
### Prerequisites
You must have the following applications installed before proceeding. If you are missing any one of these then you cannot begin.

* ``Python 3.6``
* ``brew``
* ``virtualenv``
* ``redis``
* ``PostGres``

#### Installation
The following section explains how to setup the application.

1. Clone a copy of the project somewhere on your machine, we'll be saving to the following locaiton.

  ```
  mkdir ~/Developer/nwapp/;
  cd ~/Developer/nwapp/
  git clone https://github.com/nwatchcanada/nwapp-back;
  cd ~/Developer/over55/nwapp-back
  ```


2. Setup our virtual environment

  ```
  virtualenv -p python3.6 env
  ```


3. Now lets activate virtual environment

  ```
  source env/bin/activate
  ```


4. Now lets install the libraries this project depends on.

  ```
  pip install -r requirements.txt
  ```

#### Database Setup
This project uses the ``PostGres`` database and as a result requires setup before running. The following instructions are to be run in your ``PostGres`` console:

  ```sql
  drop database nwapp_db;
  create database nwapp_db;
  \c nwapp_db;
  CREATE USER django WITH PASSWORD '123password';
  GRANT ALL PRIVILEGES ON DATABASE nwapp_db to django;
  ALTER USER django CREATEDB;
  ALTER ROLE django SUPERUSER;
  CREATE EXTENSION postgis;
  ```


#### Environment Variables Setup
1. Populate the environment variables for our project.

  ```
  ./setup_credentials.sh
  ```

2. Go inside the environment variables.

  ```
  vi ./nwapp/nwapp/.env
  ```

3. Edit the file to suite your needs.

#### Final Setup
Run the following commands to populate the database.
  ```
  cd ../nwapp/nwapp-back/nwapp;
  python manage.py makemigrations; \
  python manage.py migrate_schemas; \
  python manage.py init_app; \
  python manage.py setup_oauth2; \
  python manage.py create_shared_user "bart@mikasoftware.com" "123password" "Bart" "Mika";
  ```

#### Host File Setup
This project is uses ``django-tenants`` library and is setup to work with multiple domains. As a result, we will need to bind the address **nwapp.ca** to your ``localhost``. To do this follow these instructions.

1. Update your hosts file to support our applications domain.

  ```
  sudo vi /etc/hosts
  ```

2. Append to the file...

  ```
  127.0.0.1       nwapp.ca
  127.0.0.1       nwapp.ca
  127.0.0.1       london.nwapp.ca
  127.0.0.1       london.nwapp.ca
  ```


3. Refresh the dns on your machine to support our new domains.

  ```
  dscacheutil -flushcache
  ```

## Usage
To run the web-app, you’ll need to run the server instance and access the page from your browser.

Start up the web-server:

  ```
  sudo python manage.py runserver nwapp.ca:80
  ```

And inside another seperate ``Terminal`` console, please run:

  ```
  python manage.py rqworker
  ```

Finally, in your web-browser, load up the following url:

  ```
  http://nwapp.ca/
  ```

Congratulations, you are all setup to run the web-app! Have fun coding!#
