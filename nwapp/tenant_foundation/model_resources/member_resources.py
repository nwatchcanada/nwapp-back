from faker import Faker

from shared_foundation.models import SharedUser, SharedGroup
from tenant_foundation.models import Member
from tenant_foundation.models import MemberAddress
from tenant_foundation.models import MemberContact
from tenant_foundation.models import MemberMetric
from tenant_foundation.models import MemberComment


def seed_members(tenant, length=25):
    results = []
    faker = Faker('en_CA')
    for i in range(0,length):
        try:
            first_name = faker.first_name()
            last_name = faker.last_name()
            user = SharedUser.objects.create(
                tenant=tenant,
                email = faker.safe_email(),
                first_name = first_name,
                middle_name = None,
                last_name = last_name,
            )
            user.groups.add(SharedGroup.GROUP_MEMBERSHIP.MEMBER)
            member = Member.objects.create(
                user=user,
                type_of=Member.MEMBER_TYPE_OF.RESIDENTIAL
            )
            member_contact = MemberContact.objects.create(
                member=member,
                is_ok_to_email=True,
                is_ok_to_text=True,
                # organization_name="",
                # organization_type_of=
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                primary_phone=faker.phone_number(),
                secondary_phone=faker.phone_number(),
            )
            member_address = MemberAddress.objects.create(
                member=member,
                country="Canada",
                region="Ontario",
                locality=faker.city(),
                street_number=faker.pyint(min_value=1, max_value=1000, step=1),
                street_name=faker.street_name(),
                apartment_unit=faker.pyint(min_value=1, max_value=1000, step=1),
                street_type=MemberAddress.STREET_TYPE.OTHER,
                street_type_other="Highway",
                street_direction=MemberAddress.STREET_DIRECTION.NONE,
                postal_code=faker.postalcode(),
            )
            member_metric = MemberMetric.objects.create(
                member=member,
                # how_did_you_hear=
                # how_did_you_hear_other=
                # expectation=
                # expectation_other=
                # meaning=
                # meaning_other=
                # gender=
                # willing_to_volunteer=
                # another_household_member_registered=
                # year_of_birth=
                # total_household_count=
                # over_18_years_household_count=
                # organization_employee_count=
                # organization_founding_year=
            )
            results.append(member)
        except Exception as e:
            print(e)
            pass
    return results
