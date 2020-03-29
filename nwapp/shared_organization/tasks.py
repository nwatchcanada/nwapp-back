import requests
import logging
from django.conf import settings
from django.db import transaction
from django_rq import get_queue, get_worker
from django_rq import job
from django.core.management import call_command
from rq import get_current_job

from shared_foundation import constants
from shared_foundation.models import (
    SharedOrganization,
    SharedOrganizationDomain
)


logger = logging.getLogger(__name__)


@job
@transaction.atomic
def create_organization_func(validated_data):
    """
    Background function will take the parameter dictionary and use it
    generate our schema in the database.
    """
    schema_name = validated_data.get('schema_name', None)
    alternate_name = validated_data.get('alternate_name', None)
    name = validated_data.get('name', None)
    description = validated_data.get('description', False)
    country = validated_data.get('country', None)
    city = validated_data.get('city', None)
    province = validated_data.get('province', None)
    street_number = validated_data.get('street_number', None)
    street_name = validated_data.get('street_name', None)
    apartment_unit = validated_data.get('apartment_unit', None)
    street_type = validated_data.get('street_type', None)
    street_type_other = validated_data.get('street_type_other', None)
    street_direction = validated_data.get('street_direction', None)
    postal_code = validated_data.get('postal_code', None)
    timezone_name = validated_data.get('timezone_name', None)
    police_report_url = validated_data.get('police_report_url', None)
    default_position = validated_data.get('default_position', None)
    default_zoom = validated_data.get('default_zoom', None)

    if street_type == "" or street_type == None:
        street_type = "-"
    if street_type_other == "" or street_type_other == None:
        street_type_other = "-"
    if street_direction == "" or street_direction == None:
        street_direction = "-"

    # For debugging purposes only.
    print(
        "\nschema_name", schema_name,
        "\nname", name,
        "\nalternate_name", alternate_name,
        "\ndescription", description,
        "\ncountry", country,
        "\ncity", city,
        "\nprovince", province,
        "\nstreet_number", street_number,
        "\nstreet_name", street_name,
        "\napartment_unit", apartment_unit,
        "\nstreet_type", street_type,
        "\nstreet_type_other", street_type_other,
        "\nstreet_direction", street_direction,
        "\npostal_code", postal_code,
        "\ntimezone_name", timezone_name,
        "\npolice_report_url", police_report_url,
        "\default_position", default_position,
        "\default_zoom", default_zoom,
        "\n"
    )

    # Create your tenant in the database.
    tenant = SharedOrganization(
        schema_name=schema_name,
        name=name,
        alternate_name=alternate_name,
        description=description,
        country=country,
        city=city,
        province=province,
        street_number=street_number,
        street_name=street_name,
        apartment_unit=apartment_unit,
        street_type=street_type,
        street_type_other=street_type_other,
        street_direction=street_direction,
        postal_code=postal_code,
        timezone_name=timezone_name,
        police_report_url=police_report_url,
        default_position=default_position,
        default_zoom=default_zoom
    )
    tenant.save()

    get_worker().work(burst=True) # Processes all BACKGROUND jobs in FOREGROUND then stop. (Note: https://stackoverflow.com/a/12273705)

    # Add one or more domains for the tenant
    domain = SharedOrganizationDomain()
    domain.domain = settings.NWAPP_BACKEND_HTTP_DOMAIN
    domain.domain = tenant.schema_name + '.' + settings.NWAPP_BACKEND_HTTP_DOMAIN
    domain.tenant = tenant
    domain.is_primary = False
    domain.save()

    get_worker().work(burst=True) # Processes all BACKGROUND jobs in FOREGROUND then stop. (Note: https://stackoverflow.com/a/12273705

    # Populate our new organization tenant with post-creation data.
    call_command('populate_tenant_content', schema_name, verbosity=0)
