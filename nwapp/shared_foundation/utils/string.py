from django.utils.crypto import get_random_string


def get_referral_code(max_length=31):
    return get_random_string(
        length=max_length,
        allowed_chars='abcdefghijkmnpqrstuvwxyz'
                      'ABCDEFGHIJKLMNPQRSTUVWXYZ'
                      '23456789'
    )


def pretty_dt_string(dt):
    """
    Utility function will convert the naive/aware datatime to a pretty datetime
    format which will work well for output.
    """
    if dt is None:
        return None

    try:
        dt = dt.replace(microsecond=0)
        dt = dt.replace(second=0)
        dt_string = dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        dt_string = dt.strftime("%Y-%m-%d")
    return dt_string
