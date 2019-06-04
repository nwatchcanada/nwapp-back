
# How to use MessagePack with Django REST Framework and Axios
## Part 1 of 2: Django Backend
### 1. Setup Project
1. Go to the [django-rest-framework-msgpack](https://github.com/juanriaza/django-rest-framework-msgpack) library and have a look around. This is the main library we will be using to implement the ``MessagePack`` serializing and deseerializing. Just spend time reading the developer documentation.

2. Setup our ``Django`` example project by running the following:

  ```bash
  virtualenv -p python3.6 env
  source env/bin/activate
  pip install django
  python django_admin startproject msgpackserver
  cd msgpackserver
  ```

2. Install our [Django REST Framework]() library and our [Django Rest Framework Msgpack](https://github.com/juanriaza/django-rest-framework-msgpack)  extention to support ``MessagePack``.

  ```bash
  pip install djangorestframework
  pip install djangorestframework-msgpack
  ```

3. Configure our settings to look more-or-less like this.

  ```python
  # msgpackserver/msgpackserver/settings.py

  ...

  INSTALLED_APPS = [

  ...

  'rest_framework',
  ]

  ...

  # DEVELOPERS NOTE:
  # - We are able to add different kind of parsers/renders into
  #   Django REST and decide which ones to use when the client
  #   makes calls.
  # - We use set the `Content-Type` and `Accept` in the header
  #   to let Django REST know which parser/render to use.

  REST_FRAMEWORK = {
      'DEFAULT_RENDERER_CLASSES': [
          'rest_framework.renderers.JSONRenderer',
          'rest_framework_msgpack.renderers.MessagePackRenderer',
      ],
      'DEFAULT_PARSER_CLASSES': [
          'rest_framework.parsers.JSONParser',
          'rest_framework_msgpack.parsers.MessagePackParser',
      ],
  }
  ```

### 2. Setup App

1. Run the following command to create our app.

  ```
  python manage.py startapp api
  ```

2. Update our ``settings.py`` file to look like this:

  ```python
  # msgpackserver/msgpackserver/settings.py

  ...

  INSTALLED_APPS = [

  ...

  'rest_framework',
  'api',
  ]
  ```

3. Create our ``urls.py`` file and populate it with the following code:

  ```python
  # msgpackserver/api/urls.py

  from django.urls import path

  from api.views import *
  urlpatterns = (
      path('api/hello', HellowAPIView.as_view(), name='hello_api_endpoint'),
  )
  ```

4. Finally make sure our ``api/urls.py`` is registered.

  ```python
  # msgpackserver/msgpackserver/urls.py

  from django.contrib import admin
  from django.conf.urls.i18n import i18n_patterns
  from django.urls import path, include # This needs to be added

  urlpatterns = ([
      # Allow the following apps for being accessed without language string.
      path('', include('shared_foundation.urls')),
      path('', include('api.urls')),
  ])

  # Add support for language specific context URLs.
  urlpatterns += i18n_patterns(
      path('admin/', admin.site.urls),
      path('', include('api.urls')),
      prefix_default_language=True
  )
  ```

### 3. Create API endpoint using ``MessagePack``

Copy and past the following code into your ``msgpackserver/api/views.py`` file:

```python
# msgpackserver/api/views.py

# -*- coding: utf-8 -*-
from rest_framework.views import APIView
from rest_framework.response import Response

class HelloAPIView(APIView):
    throttle_classes = ()
    permission_classes = ()

    def post(self, request):
        name = request.data.get('name', None)
        return Response(data={
            'details': 'Hello ' + name
        }, status=status.HTTP_200_OK)
```

## Part 2 of 2: Javascript Frontend - Axios

1. We will be using the [msgpack-lite](https://github.com/kawanet/msgpack-lite) library. Please spend some time reviewing their documentation.

2. Also if you haven't already read the documentation, please read the [axios](https://github.com/axios/axios) documentation.

3. Install our dependencies

  ```bash
  npm install --save axios
  npm install --save msgpack-lite
  ```

2. The follow code will work.

  ```javascript
  import axios from 'axios';
  import msgpack from 'msgpack-lite';

  export function postHello() {
      return dispatch => {
          // Create a new Axios instance which will be sending and receiving in
          // MessagePack (Buffer) format.
          const customAxios = axios.create({
              headers: {
                  'Content-Type': 'application/msgpack;', // (1)
                  'Accept': 'application/msgpack',        // (2)
              },
              responseType: 'arraybuffer'                 // (3)
          })

          // DEVELOPER NOTES:
          // (1) By setting the value to ``application/msgpack`` we are telling
          //     ``Django REST Framework`` to use our ``MessagePack`` library.
          // (2) Same as (1)
          // (3) We are telling ``Axios`` that the data returned from our server
          //     needs to be in ``arrayBuffer`` format so our ``msgpack-lite``
          //     library can decode it. Special thanks to the following link:
          //     https://blog.notabot.in/posts/how-to-use-protocol-buffers-with-rest

          // Encode from JS Object to MessagePack (Buffer)
          var buffer = msgpack.encode({
              'name': 'Bartlomiej Mika',
          });

          customAxios.post("http://localhost:8000/api/hello", buffer).then( (successResponse) => {
              // Decode our MessagePack (Buffer) into JS Object.
              const responseData = msgpack.decode(Buffer(successResponse.data));

              // You should see your output in the console! :)
              console.log(responseData);

          }).catch( (errorResponse) => {
              // Decode our MessagePack (Buffer) into JS Object.
              const responseData = msgpack.decode(Buffer(errorResponse.data));

              // You should see your output in the console! :(
              console.log(responseData);

          }).then( () => {
              // Do nothing.
          });

      }
  }
  ```

5. Happy coding!
