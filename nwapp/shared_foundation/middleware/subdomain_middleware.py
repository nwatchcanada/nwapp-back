
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

        domain_parts = request.get_host().split('.')
        subdomain = "www"
        if(len(domain_parts) >= 2):
            subdomain = domain_parts[0].lower()
        request.subdomain = subdomain

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
