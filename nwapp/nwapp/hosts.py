from django.conf import settings
from django_hosts import patterns, host


host_patterns = patterns('',
    host(r'www', settings.ROOT_URLCONF, name='www'),  # <-- The `name` we used to in the `DEFAULT_HOST` setting
    host(r'admin', settings.ROOT_URLCONF, name='admin'),
    # host(r'(\w+)', 'tenant_district.urls', name='tenant_district'),
    host(r'(\w+)', 'api.urls', name='wildcard'),
)
