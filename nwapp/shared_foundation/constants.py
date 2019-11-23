import pytz


TIMEZONE_CHOICES = tuple(zip(pytz.all_timezones, pytz.all_timezones))


COUNTRY_PROVINCE_CODES = {
    'Canada': {
        'Newfoundland and Labrador': 'NL',
        'Prince Edward Island': 'PE',
        'Nova Scotia': 'NS',
        'New Brunswick': 'NB',
        'Quebec': 'QC',
        'Ontario': 'ON',
        'Manitoba': 'MB',
        'Saskatchewan': 'SK',
        'Alberta': 'AB',
        'British Columbia': 'BC',
        'Yukon': 'YT',
        'Northwest Territories': 'NT',
        'Nunavut': 'NU',
    },
}


# The groups of our application.
#

EXECUTIVE_GROUP_ID = 1
MANAGEMENT_GROUP_ID = 2
FRONTLINE_GROUP_ID = 3
ASSOCIATE_GROUP_ID = 4
AREA_COORDINATOR_GROUP_ID = 5
MEMBER_GROUP_ID = 6
