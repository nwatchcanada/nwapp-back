## Version
Returns the version information of Comics Cantina. This is a useful endpoint to call when you are setting up your project and you want to confirm you are able to communicate with the web-service.


* **URL**

        /api/v1/version


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

        $ http get localhost:80/api/v1/version
