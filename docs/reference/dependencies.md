This article explains the libraries that our project uses. Before you begin, be sure to setup the virtual envrionment:

```
virtualenv -p python3.6 env
source env/bin/activate
```


When trying to install ``psycopg2`` on ``MacOS``, please make sure to run the following. Special thanks to the [this link](https://stackoverflow.com/a/57617813).

```
export PATH="/usr/local/opt/openssl/bin:$PATH"
export LDFLAGS="-L/usr/local/opt/curl/lib -L/usr/local/opt/openssl/lib"
export CPPFLAGS="-I/usr/local/opt/curl/include -I/user/local/opt/openssl/include"
```

The following are a complete list of all the third-party library and frameworks our project is using.

```
pip install django                        # Our MVC Framework
pip install django-environ                # Environment Variables with 12factorization
pip install django-tenants                # Django tenants using PostgreSQL Schemas
pip install Pillow                        # Req: ImageField
pip install django-ipware                 # Best attempt to get IP address while keeping it DRY.
pip install Faker                         # Library that generates fake data for you.
pip install django-rq                     # Redis Queue Library
pip install django-redis-cache            # Django cache backend powered by Redis
pip install rq-scheduler                  # Redis Queue Scheduler Library
pip install django-cors-headers           # Enable CORS in Headers
pip install gunicorn                      # Web-Server Helper
pip install djangorestframework           # RESTful API Endpoint Generator
pip install djangorestframework-msgpack   # MessagePack support for Django REST framework
pip install django-extra-fields           # Django REST Framework extensions
pip install django-filter                 # Filtering Django QuerySets based on user selections
pip install python-dateutil               # Useful extensions to the standard Python datetime features
pip install django-anymail[mailgun]       # Third-Party Email
pip install django-oauth-toolkit          # oAuth 2.0 Client and Provider Framework


pip install django-money                  # Money fields for django forms and models.
pip install freezegun                     # Python datetime override library
pip install django-storages               # Collection of custom storage backends for Django.
pip install boto3                         # AWS S3 Bindings
```

DigitalOcean Tutorials:
* [How To Create a DigitalOcean Space and API Key](https://www.digitalocean.com/community/tutorials/how-to-create-a-digitalocean-space-and-api-key)
* [How To Set Up Object Storage with Django](https://www.digitalocean.com/community/tutorials/how-to-set-up-object-storage-with-django)
* [How to Set Up a Scalable Django App with DigitalOcean Managed Databases and Spaces](https://www.digitalocean.com/community/tutorials/how-to-set-up-a-scalable-django-app-with-digitalocean-managed-databases-and-spaces)
