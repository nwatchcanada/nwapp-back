## Dashboard
Returns the dashboard data for your account.

* **URL**

        /api/v1/dashboard


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

        $ http get tenant.localhost:80/api/v1/dashboard Authorization:"Bearer $NWAPP_BACK_API_TOKEN"
