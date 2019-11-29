from django.core.validators import RegexValidator

"""
Source for the following regix: https://stackoverflow.com/a/19131360
"""
e164_phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
