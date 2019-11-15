NWApp API Web-Service Reference (Dashboard)
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
  $ http get london.localhost:80/api/v1/dashboard Authorization:"Bearer $NWAPP_BACK_API_TOKEN"
  ```
