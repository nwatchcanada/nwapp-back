# nwapp-back
[![Documentation Status](https://readthedocs.org/projects/nwapp-docs/badge/?version=latest)](https://nwapp-docs.readthedocs.io/en/latest/?badge=latest)

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
  mkdir ~/go/src/github.com/nwatchcanda;
  cd ~/go/srcgithub.com/nwatchcanda;
  git clone https://github.com/nwapp/nwapp-back.git;
  cd nwapp-back
  ```

#### Database Setup
This project uses the ``PostGres`` database and as a result requires setup before running. The following instructions are to be run in your ``PostGres`` console:

  ```sql
  drop database nwapp_golang_db;
  create database nwapp_golang_db;
  \c nwapp_golang_db;
  CREATE USER django WITH PASSWORD '123password';
  GRANT ALL PRIVILEGES ON DATABASE nwapp_golang_db to django;
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

## Contact

Do you have any questions? Join our [mailing list](https://groups.google.com/forum/#!forum/nwl-app) and ask your questions there.
