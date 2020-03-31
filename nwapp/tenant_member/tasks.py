import requests
# import logging
from rq import get_current_job
from django_rq import job
from django.core.management import call_command

from shared_foundation.utils import get_point_from_ip


# logger = logging.getLogger(__name__)


@job
def geocode_member_address_func(schema_name, member_slug):
    call_command('geocode_member_address', schema_name, member_slug, verbosity=0)


@job
def geoip2_member_audit_func(schema_name, member_slug):
    call_command('geoip2_member_audit', schema_name, member_slug, verbosity=0)
