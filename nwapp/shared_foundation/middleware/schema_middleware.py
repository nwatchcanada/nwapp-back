from django.core.cache import cache

from shared_foundation.models import SharedOrganization


class SchemaMiddleware:
    """
    Middleware responsible for attaching the schema to every request made
    to our system, if a schema type of request was made.

    This middleware is dependent on the ``django-hosts`` library to work.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        # STEP 1:
        # Use `django-hosts` to check the host & schema, then extract
        # the schema value.
        domain_parts = request.get_host().split('.')
        schema = "www"
        if(len(domain_parts) >= 2):
            schema = domain_parts[0].lower()

        # STEP 2:
        # Lookup the schema in the cache
        tenant = cache.get(schema)
        if tenant is None:
            tenant = SharedOrganization.objects.filter(schema=schema).first()
            if tenant:
                print("SchemaMiddleware | Cached:", schema)
                cache.set(schema, tenant, None)

        # STEP 3:
        # Attach the `tenant` and `schema` to the `request`.
        request.schema = schema
        request.tenant = tenant

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
