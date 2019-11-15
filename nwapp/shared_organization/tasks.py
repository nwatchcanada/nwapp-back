import requests
import logging
from rq import get_current_job
from django_rq import job
from django.core.management import call_command


logger = logging.getLogger(__name__)


@job
def create_organization_func(validated_data):
    alternate_name = validated_data.get('alternate_name', None)
    name = validated_data.get('name', None)
    description = validated_data.get('description', False)
    country = validated_data.get('country', None)
    locality = validated_data.get('locality', None)
    region = validated_data.get('region', None)
    schema_name = validated_data.get('schema_name', None)
    # until_date = validated_data.get('until_date', None)
    timezone_name = validated_data.get('timezone_name', None)
    call_command(
        'create_organization',
        schema_name,
        name,
        alternate_name,
        description,
        country,
        locality,
        region,
        timezone_name,
        verbosity=0
    )
