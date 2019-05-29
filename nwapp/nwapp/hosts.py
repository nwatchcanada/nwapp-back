from django.conf import settings
from django_hosts import patterns, host


host_patterns = patterns('',
    host(None, settings.ROOT_URLCONF, name="index"),
    host(r'www', settings.ROOT_URLCONF, name='www'),
    host(r'admin', settings.ROOT_URLCONF, name='admin'),
    # host(r'(\w+)', 'tenant_district.urls', name='tenant_district'),
    host(r'(\w+)', 'api.urls', name='wildcard'),
)
