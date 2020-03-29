import requests
import logging
from rq import get_current_job
from django_rq import job
from django.core.management import call_command


logger = logging.getLogger(__name__)


@job
def process_associate_with_slug_func(schema_name, slug):
    call_command('process_associate_with_slug', schema_name, slug, verbosity=0)


@job
def geocode_associate_address_func(schema_name, slug):
    call_command('geocode_associate_address', schema_name, slug, verbosity=0)
