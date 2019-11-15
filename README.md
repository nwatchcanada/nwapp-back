# nwapp-back
Online aquaponics / hydroponic device monitoring portal implemented in Python and powered by Django.


## Instructions
### Prerequisites
You must have the following applications installed before proceeding. If you are missing any one of these then you cannot begin.

* ``Python 3.7``
* ``virtualenv``
* ``redis``
* ``Postgres 10``

#### Installation
The following section explains how to setup the application.

1. Clone a copy of the project somewhere on your machine, we'll be saving to the following locaiton.

  ```
  mkdir ~/python/github.com/nwatchcanda;
  cd ~/python/github.com/nwatchcanda;
  git clone https://github.com/nwapp/nwapp-back.git;
  cd nwapp-back
  ```


2. Setup our virtual environment

  ```
  virtualenv -p python3.7 env
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

### Finalization.

1. Run the following. **Please change the password to your own.**

  ```
  redis-cli FLUSHDB;
  python manage.py makemigrations
  python manage.py migrate
  python manage.py migrate_schemas --executor=multiprocessing
  python manage.py init_app
  python manage.py create_admin_user "bart@mikasoftware.com" "123password" "Bart" "Mika";
  python manage.py setup_resource_server_authorization
  python manage.py collectstatic
  ```

2. Register the app with the following social-auth services. Also read [this tutorial](https://simpleisbetterthancomplex.com/tutorial/2016/10/24/how-to-add-social-login-to-django.html) on setting these up.

    ```
    https://github.com/settings/applications/new
    https://apps.twitter.com/
    https://facebook.com/
    ```
