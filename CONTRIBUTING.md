# Contributing to Neigbhourhood Watch App

## Do you have questions about the source code?

* Ask any question about how to use Neigbhourhood Watch App in the [nwl-app mailing list](https://groups.google.com/forum/#!forum/nwl-app).

## Do you intend to add a new feature or change an existing one?
* Suggest your change in the [nwl-app mailing list](https://groups.google.com/forum/#!forum/nwl-app). and start writing code.

* Do not open an issue on GitHub until you have collected positive feedback about the change. GitHub issues are primarily intended for bug reports and fixes.

## What libraries does this project use?
Here are the libraries that this project utilizes, please update this list as
new libraries get added.

```bash
pip install pytz                          # World Timezone Definitions
pip install django                        # Our MVC Framework
pip install django-environ                # Environment Variables with 12factorization
pip install django-cors-headers           # Enable CORS in Headers
pip install psycopg2-binary               # Postgres SQL ODBC
pip install django-oauth-toolkit          # oAuth 2.0 Client and Provider Framework
pip install Pillow                        # Req: ImageField
pip install djangorestframework           # RESTful API Endpoint Generator
pip install django-extra-fields           # Django REST Framework extensions
pip install djangorestframework-msgpack   # Message Pack Support for Django REST
pip install gunicorn                      # Web-Server Helper
pip install django-filter                 # Generic system for filtering Django QuerySets based on user selections
pip install django-rq                     # Redis Queue Library
pip install rq-scheduler                  # Redis Queue Scheduler Library
pip install django-redis-cache            # Django cache backend powered by Redis
pip install python-dateutil               # Useful extensions to the standard Python datetime features
pip install django-anymail[mailgun]       # Third-Party Email
pip install django-ipware                 # Best attempt to get IP address while keeping it DRY.
pip install django-money                  # Money fields for django forms and models.
pip install Faker                         # Library that generates fake data for you.
pip install freezegun                     # Python datetime override library
pip install django-storages               # Collection of custom storage backends for Django.
pip install boto3                         # AWS S3 Bindings
```

## Any useful tutorials?

* [How To Create a DigitalOcean Space and API Key](https://www.digitalocean.com/community/tutorials/how-to-create-a-digitalocean-space-and-api-key)
* [How To Set Up Object Storage with Django](https://www.digitalocean.com/community/tutorials/how-to-set-up-object-storage-with-django)
* [How to Set Up a Scalable Django App with DigitalOcean Managed Databases and Spaces](https://www.digitalocean.com/community/tutorials/how-to-set-up-a-scalable-django-app-with-digitalocean-managed-databases-and-spaces)



## What coding conventions should I use?

1. Please use [container-component pattern](https://medium.com/@learnreact/container-components-c0e67432e005) when creating new pages / views / etc.

2. In the container, please add the following comments to help organization. The following is an example of how it should be organized:

    ```javascript
    import React from 'react';
    import { connect } from 'react-redux';

    import RegisterSuccessComponent from '../../../components/account/register/registerSuccessComponent';


    class RegisterSuccessContainer extends React.Component {

        /**
         *  Initializer
         *------------------------------------------------------------
         */

        /**
         *  Utility
         *------------------------------------------------------------
         */

        /**
         *  Component Life-cycle Management
         *------------------------------------------------------------
         */

        /**
         *  API callback functions
         *------------------------------------------------------------
         */

        /**
         *  Event handling functions
         *------------------------------------------------------------
         */

        /**
         *  Main render function
         *------------------------------------------------------------
         */

        componentDidMount() {
            window.scrollTo(0, 0);  // Start the page at the top of the page.
        }

        render () {
            return (
                <RegisterSuccessComponent />
            )
        }
    }

    const mapStateToProps = function(store) {
        return {
            user: store.userState
        };
    }

    const mapDispatchToProps = dispatch => {
        return {

        }
    }

    export default connect(
        mapStateToProps,
        mapDispatchToProps
    )(RegisterSuccessContainer);
    ```

3. Please use ``camelCase`` text for all javascript code and use ``snake_case`` text when dealing with our API.

4. Please ue 4 line white characters for a 1 single tab.

5. When using ``localStorage`` please add the ``nwapp`` namespace to every key name.
