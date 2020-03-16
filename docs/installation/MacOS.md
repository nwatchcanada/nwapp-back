The goal of this article is to provide step-by-step instructions on how to setup [nwapp-back](https://github.com/nwatchcanada/nwapp-back) on your ``MacOS`` local machine.

# 1. Prerequisites
You must have the following applications installed before proceeding. If you are missing any one of these then you cannot begin.

* ``Python 3.6``
* ``brew``
* ``virtualenv``
* ``redis``
* ``PostGres``

# 2. Code Setup
The following section explains how to setup the application.

(1) Clone a copy of the project somewhere on your machine, we'll be saving to the following locaiton.

```bash
git clone https://github.com/nwatchcanada/nwapp-back;
cd nwapp-back
```

(2) Setup our virtual environment

```bash
virtualenv -p python3.6 env
```

(3) Now lets activate virtual environment

```bash
source env/bin/activate
```

(4) Now lets install the libraries this project depends on.

```bash
pip install -r requirements.txt
```

# 3. Database Setup
This project uses the ``Postgres`` database and as a result requires setup before running. The following instructions are to be run in your ``Postgres`` console:

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
**Please make sure you change your password if you use this code in production.**


# 4. Environment Variables Setup
(1) Populate the environment variables for our project.

```bash
./setup_credentials.sh
```

(2) Go inside the environment variables.

```bash
vi ./nwapp/nwapp/.env
```

(3) Edit the file to suite your needs.


# 5. Final Setup

Run the following commands to finalize our project.

```bash
redis-cli FLUSHDB;
python manage.py makemigrations; \
python manage.py migrate_schemas --executor=multiprocessing; \
python manage.py init_app; \
python manage.py setup_oauth2; \
python manage.py create_shared_user "bart@mikasoftware.com" "123password" "Bart" "Mika";
python manage.py collectstatic
```

Optional commands if you want your own tenant data pre-made:

```bash
python manage.py create_shared_organization london \
       "Neighbourhood Watch London" \
       "NWatch App" \
       "This is our main tenant organization" \
       "Canada" \
       "London" \
       "Ontario" \
       "200" \
       "Centre" \
       "23" \
       "1" \
       "" \
       "" \
       "N6J4X4" \
       "America/Toronto";
python manage.py create_random_district "london" 50;
python manage.py create_random_watch "london" 250;
python manage.py create_random_member "london" 250;
python manage.py create_random_area_coordinator "london" 100;
python manage.py create_random_associate "london" 100;
python manage.py create_random_task_item "london" 250;
```

# 6. Host File Setup
This project is uses ``django-tenants`` library and is setup to work with multiple domains. As a result, we will need to bind the address **nwapp.ca** to your ``localhost``. To do this follow these instructions.

1. Update your hosts file to support our applications domain.

  ```
  sudo vi /etc/hosts
  ```

2. Append to the file...

  ```
  127.0.0.1       localhost
  127.0.0.1       london.localhost
  127.0.0.1       tenant.localhost
  ```


3. Refresh the dns on your machine to support our new domains.

  ```
  dscacheutil -flushcache
  ```

# 7. Usage
To run the web-app, you’ll need to run the server instance and access the page from your browser.

(1) Start up the web-server:

```bash
sudo python manage.py runserver localhost:80
```

(2) And inside another seperate ``Terminal`` console, please run:

```bash
python manage.py rqworker
```

(3) And inside another seperate ``Terminal`` console, please run:

```bash
python manage.py rqscheduler
```

(4) Finally, in your web-browser, load up the following url:

```
http://localhost:80
```

(4) Congratulations, you are all setup to run the web-app! Have fun coding!
