from django.contrib.gis.geoip2 import GeoIP2
from django.contrib.gis.geos import Point


def get_point_from_ip(ip_address):
    """
    Utility function will lookup the IP address in our `GeoIP2` database and
    return a `Point` object.
    """
    try:
        g = GeoIP2()
        if ip_address != "127.0.0.1" and ip_address != "localhost":
            client_info = g.city(ip_address)
            return Point(client_info['latitude'], client_info['longitude'])
    except Exception as e:
        print("get_point_from_ip | ip:", ip_address, "| e:", e)
    return None

    # TODO: Update documentation to support our `GeoIP2` library
    # TODO: Use a background function to handle looking up lat/long.
