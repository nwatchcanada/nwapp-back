NWApp API Web-Service Reference
======

## Developers Notes

1. To help make the next few API endpoints easy to type, save your token to the console.

    ```bash
    NWAPP_BACK_API_TOKEN='YOUR_TOKEN'
    ```

2. You will notice ``http`` used in the sample calls through this document, this is the ``Python`` command line application called ``HTTPie``. Download the command line application by following [these instructions](https://httpie.org/).

3. If you are going to make any contributions, please make sure your edits follow the [API documentation standard](https://gist.github.com/iros/3426278) for this document; in addition, please read [Googles API Design Guide](https://cloud.google.com/apis/design/) for further consideration.


## Get API Version
Returns the version information of Comics Cantina. This is a useful endpoint to call when you are setting up your project and you want to confirm you are able to communicate with the web-service.


* **URL**

  ``/api/v1/version``


* **Method**

  ``GET``


* **URL Params**

  None


* **Data Params**

  None


* **Success Response**

  * **Code:** 200
  * **Content:**

    ```json
    {
        "Service": "v0.1",
        "API: 'v1"
    }
    ```


* **Error Response**

  * None


* **Sample Call**

  ```bash
  $ http get localhost:80/api/v1/version
  ```


## Register (TODO: PENDING IMPLEMENTATION)
Submit registration details into our system to automatically create a *user* account. System return the *user* details and authentication *token*.

Created *user* accounts are automatically granted access to the system even though these accounts have not had their email verified. The system sends a verification email after creation and if the *user* does not verify in the allotted timespan, their account gets locked.

It's important to note that emails must be unique and passwords strong or else validation errors get returned.

* **URL**

  ``/api/v1/register``


* **Method**

  ``POST``


* **URL Params**

  None


* **Data Params**

  * email
  * password
  * first_name
  * last_name


* **Success Response**

  * **Code:** 200
  * **Content:**

    ```json
    {
        "email": "bart@mikasoftware.com",
        "first_name": "Bart",
        "last_name": "Mika",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1NDkyOTY1MDAsInVzZXJfaWQiOjF9.QN9dyWL2dlxKgkm0xbQAmnaI6_4amHcSfqUGQ6pZbxM",
        "user_id": 1
    }
    ```


* **Error Response**

  * **Code:** 400
  * **Content:**

    ```json
    {
        "error": "Email is not unique.",
        "status": "Invalid request."
    }
    ```


* **Sample Call**

  ```bash
  $ http post localhost:80/api/v1/public/register \
    email=bart@mikasoftware.com \
    password=YOUR_PASSWORD \
    first_name=Bart \
    last_name=Mika
  ```


## Login
Returns the *user profile* and authentication *token* upon successful login in.

* **URL**

  ``/api/v1/login``


* **Method**

  ``POST``


* **URL Params**

  None


* **Data Params**

  * email
  * password


* **Success Response**

  * **Code:** 200
  * **Content:**

    ```json
    {
        "access_token": {
            "expires": 1573875899,
            "scope": "read,write,introspection",
            "token": "pwtYmgPCEwNXFUhPVjVNKcEBxYgvUz"
        },
        "email": "bart@mikasoftware.com",
        "first_name": "Bart",
        "group_membership_id": 1,
        "last_name": "Mika",
        "middle_name": null,
        "refresh_token": {
            "revoked": null,
            "token": "xWGpIbdDJRcLiy4R2wEfUOuDD252cB"
        },
        "schema_name": "public"
    }
    ```


* **Error Response**

  * **Code:** 400
  * **Content:**

    ```json
    {
        "error": "Email or password is incorrect.",
        "status": "Invalid request."
    }
    ```


* **Sample Call**

  ```bash
  $ http post localhost:80/api/v1/login \
    email=bart@mikasoftware.com \
    password=YOUR_PASSWORD
  ```

* **Notes**

  * If the server returned the access token value of ``pwtYmgPCEwNXFUhPVjVNKcEBxYgvUz`` then please make sure you write in your console ``NWAPP_BACK_API_TOKEN='pwtYmgPCEwNXFUhPVjVNKcEBxYgvUz'``.


## Logout
Performs logout operation for authenticated user thus invalidating the user's ``token``.

* **URL**

  ``/api/v1/logout``


* **Method**

  ``POST``


* **URL Params**

  None


* **Data Params**

  None


* **Success Response**

  * **Code:** 200
  * **Content:**

    ```json
    {
        "detail": "You are now logged off."
    }
    ```


* **Error Response**

  None


* **Sample Call**

  ```bash
  $ http post localhost:80/api/v1/logout token=$NWAPP_BACK_API_TOKEN Authorization:"Bearer $NWAPP_BACK_API_TOKEN"
  ```

* **Notes**

  * If the server returned the access token value of ``pwtYmgPCEwNXFUhPVjVNKcEBxYgvUz`` then please make sure you write in your console ``NWAPP_BACK_API_TOKEN='pwtYmgPCEwNXFUhPVjVNKcEBxYgvUz'``.


## Get Profile
The API endpoint used to get the *user profile details*. Only the *profile* of the *authenticated user* is returned.

* **URL**

  ``/api/v1/profile``


* **Method**

  ``GET``


* **URL Params**

  None


* **Data Params**

  None


* **Success Response**

  * **Code:** 200
  * **Content:**

    ```json
    {
        "email": "bart@mikasoftware.com",
        "first_name": "Bart",
        "last_name": "Mika",
        "user_id": 1
    }
    ```


* **Error Response**

  * None


* **Sample Call**

  ```bash
  $ http get localhost:80/api/v1/profile Authorization:"Bearer $NWAPP_BACK_API_TOKEN"
  ```


## List Public Organizations (TODO: PENDING IMPLEMENTATION)
Returns paginated list of all the *organizations* which have been approved by the staff of [**Lucha Comics** ](https://luchacomics.com/) for public viewing. Anonymous users are granted permission to make calls to this endpoint.

* **URL**

  ``/api/v1/organizations``


* **Method**

  ``GET``


* **URL Params**

   * page


* **Data Params**

  None


* **Success Response**

  * **Code:** 200
  * **Content:**

  ```json
  [
      {
          "description": "The company",
          "id": 1,
          "name": "Mika Software Corporation"
      }
  ]
  ```


* **Error Response**

  * None


* **Sample Call**

  ```bash
  $ http get localhost:80/api/v1/public/organizations page==1 Authorization:"Bearer $NWAPP_BACK_API_TOKEN"
  ```


## Create Organization (TODO: PENDING IMPLEMENTATION)
Creates an *organization* by an *authenticated user* in our system. Please note the following rules:

* *User* is able to create only a single *organization* and cannot create anymore.
* *User* cannot be an employee of an *organization*.

Once an *organization* has been created, the staff of [**Lucha Comics** ](https://luchacomics.com/) must approve the *organization* before it becomes publicly viewable on Comics Cantina.

* **URL**

  ``/api/v1/organizations``


* **Method**

  ``POST``


* **URL Params**

  None


* **Data Params**

    * name
    * description
    * email
    * street_address
    * street_address_extra
    * city
    * province
    * country
    * currency - optional
    * language - optional
    * website - optional
    * phone - optional
    * fax - optional


* **Success Response**

  * **Code:** 200
  * **Content:**

    ```json
    {
        "city": "London",
        "country": "Canada",
        "description": "The company",
        "email": "bart@mikasoftware.com",
        "id": 1,
        "name": "Mika Software Corporation",
        "owner_id": 1,
        "province": "Ontario",
        "status": 1,
        "street_address": "111-204 Infinite Loop Road"
    }
    ```


* **Error Response**

  * **Code:** 400
  * **Content:**

    ```json
    {
        "error": "Name is not unique.",
        "status": "Invalid request."
    }
    ```

  OR

  * **Code:** 400
  * **Content:**

    ```json
    {
        "error": "Cannot create organization because you have already created an organization. You are allowed to only have one organization per account.",
        "status": "Invalid request."
    }
    ```

  OR

  * **Code:** 400
  * **Content:**

    ```json
    {
        "error": "Cannot create organization because you are an employee. Please create a new account if you want to create an organization.",
        "status": "Invalid request."
    }
    ```


* **Sample Call**

  ```bash
  $ http post localhost:80/api/v1/organizations \
    Authorization:"Bearer $NWAPP_BACK_API_TOKEN" \
    name="Mika Software Corporation" \
    description="The company" \
    email="bart@mikasoftware.com" \
    street_address="111-204 Infinite Loop Road" \
    city="London" province="Ontario" country="Canada"
  ```


## List Organizations (TODO: PENDING IMPLEMENTATION)
Returns paginated list of all the *organizations* if the *authenticated user* is a staff member of [**Lucha Comics** ](https://luchacomics.com/).

* **URL**

  ``/api/v1/organizations``


* **Method**

  ``GET``


* **URL Params**

  * page


* **Data Params**

  None


* **Success Response**

  * **Code:** 200
  * **Content:**

    ```json
    [
        {
            "description": "The company",
            "id": 1,
            "name": "Mika Software Corporation"
        }
    ]
    ```


* **Error Response**

  * **Code:** 401
  * **Content:**

    ```json
    You are not a staff member.
    ```


* **Sample Call**

  ```bash
  $ http get localhost:80/api/v1/organizations page==1 Authorization:"Bearer $NWAPP_BACK_API_TOKEN"
  ```


## Retrieve Organization (TODO: PENDING IMPLEMENTATION)
Returns the *organization* details. Only *authenticated users* which meet the following criteria are allowed to access this endpoint:

  * *user* is the owner of the *organization*
  * *user* is an employee of the *organization*

It is important to note that if the *authenticated user* is staff member of [**Lucha Comics** ](https://luchacomics.com/) then they are automatically granted access.

* **URL**

  ``/api/v1/organization/<organization_id>``


* **Method**

  ``GET``


* **URL Params**

  None


* **Data Params**

  None


* **Success Response**

  * **Code:** 200
  * **Content:**

    ```json
    {
        "city": "London",
        "country": "Canada",
        "description": "The company",
        "email": "bart@mikasoftware.com",
        "id": 1,
        "name": "Mika Software",
        "owner_id": 1,
        "province": "Ontario",
        "status": 1,
        "street_address": "111-204 Infinite Loop Road"
    }
    ```


* **Error Response**

  * None


* **Sample Call**

  ```bash
  $ http get localhost:80/api/v1/organization/1 Authorization:"Bearer $NWAPP_BACK_API_TOKEN"
  ```


## Update Organization (TODO: PENDING IMPLEMENTATION)

**TODO: IMPLEMENT**
