import requests
import logging
from rq import get_current_job
from django_rq import job
from django.core.management import call_command


logger = logging.getLogger(__name__)


@job
def process_area_coordinator_with_slug_func(schema_name, slug):
    call_command('process_area_coordinator_with_slug', schema_name, slug, verbosity=0)


@job
def geocode_area_coordinator_address_func(schema_name, slug):
    call_command('geocode_area_coordinator_address', schema_name, slug, verbosity=0)
