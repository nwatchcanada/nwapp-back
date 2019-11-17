## List Organizations
Returns the organization data for your account.

* **URL**

        /api/v1/public/organizations


* **Method**

        GET


* **URL Params**

        None


* **Data Params**

        None


* **Success Response**

    * **Code:** 200
    * **Content:**

        ```
        {
            "Service": "v0.1",
            "API: 'v1"
        }
        ```


* **Error Response**

        None


* **Sample Call**

        $ http get localhost:80/api/v1/public/organizations Authorization:"Bearer $NWAPP_BACK_API_TOKEN"


## Create Organization
Creates an *organization* by an *authenticated user* in our system. Please note the following rules:

* *User* is able to create only a single *organization* and cannot create anymore.
* *User* cannot be an employee of an *organization*.

Once an *organization* has been created, the staff of [**Neighbourhood Watch Canada** ](https://github.com/nwatchcanada) must approve the *organization* before it becomes publicly accessible.

* **URL**

  ``/api/v1/public/organizations``


* **Method**

  ``POST``


* **URL Params**

  None


* **Data Params**

    * name
    * alternate_name
    * schema_name
    * description
    * email
    * locality
    * region
    * country
    * timezone_name

* **Success Response**

  * **Code:** 200
  * **Content:**

    ```json
    {
        "locality": "London",
        "country": "Canada",
        "description": "The company",
        "email": "bart@mikasoftware.com",
        "id": 1,
        "name": "Mika Software Corporation",
        "owner_id": 1,
        "region": "Ontario",
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
  $ http post localhost:80/api/v1/public/organizations \
    Authorization:"Bearer $NWAPP_BACK_API_TOKEN" \
    name="Mika Software Corporation" \
    alternate_name="Mika Software" \
    schema_name="london" \
    description="The company" \
    email="bart@mikasoftware.com" \
    locality="London" region="Ontario" country="Canada" \
    timezone_name="America/Toronto";
  ```
