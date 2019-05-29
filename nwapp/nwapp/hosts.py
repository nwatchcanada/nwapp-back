from django.conf import settings
from django_hosts import patterns, host


host_patterns = patterns('',
    host(None, settings.ROOT_URLCONF, name="index"),
    host(r'www', settings.ROOT_URLCONF, name='www'),
    host(r'(\w+)', 'api.urls', name='wildcard'),
)
