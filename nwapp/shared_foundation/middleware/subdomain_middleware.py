from django.core.cache import cache

from shared_foundation.models import SharedOrganization


class SubdomainMiddleware:
    """
    Middleware responsible for attaching the subdomain to every request made
    to our system, if a subdomain type of request was made.

    This middleware is dependent on the ``django-hosts`` library to work.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        # STEP 1:
        # Use `django-hosts` to check the host & subdomain, then extract
        # the subdomain value.
        domain_parts = request.get_host().split('.')
        subdomain = "www"
        if(len(domain_parts) >= 2):
            subdomain = domain_parts[0].lower()

        # STEP 2:
        # Lookup the subdomain in the cache
        tenant = cache.get(subdomain)
        if tenant is None:
            tenant = SharedOrganization.objects.filter(subdomain=subdomain).first()
            if tenant:
                print("SubdomainMiddleware | Cached:", subdomain)
                cache.set(subdomain, tenant, None)

        # STEP 3:
        # Attach the `tenant` and `subdomain` to the `request`.
        request.subdomain = subdomain
        request.tenant = tenant

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
