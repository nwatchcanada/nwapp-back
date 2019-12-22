from django.utils.crypto import get_random_string


def get_referral_code(max_length=31):
    return get_random_string(
        length=max_length,
        allowed_chars='abcdefghijkmnpqrstuvwxyz'
                      'ABCDEFGHIJKLMNPQRSTUVWXYZ'
                      '23456789'
    )
