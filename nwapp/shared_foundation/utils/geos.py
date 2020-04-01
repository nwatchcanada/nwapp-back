from django.contrib.gis.geoip2 import GeoIP2
from django.contrib.gis.geos import Point
from django.contrib.gis.geos import Polygon


def get_point_from_ip(ip_address):
    """
    Utility function will lookup the IP address in our `GeoIP2` database and
    return a `Point` object.
    """
    try:
        g = GeoIP2()
        if ip_address != "127.0.0.1" and ip_address != "localhost":
            client_info = g.city(ip_address)
            return get_point_from_dict(client_info)
    except Exception as e:
        print("get_point_from_ip | ip:", ip_address, "| e:", e)
    return None


def get_point_from_dict(dict):
    """
    Utility function converts `dictionary` structured data into `Point` data.

    Example:
    INPUT: {'longitude': -81.249722, 'latitude': 42.983611}
    OUTPUT: Point(42.983611, 81.249722)
    """
    return Point(
        float(dict['latitude']),
        float(dict['longitude'])
    )


def get_point_from_arr(arr):
    """
    Utility function converts `array` structured data into `Point` data.

    Example:
    INPUT: [42.983611, -81.249722]
    OUTPUT: Point(42.983611, 81.249722)
    """
    return Point(
        float(arr[0]),
        float(arr[1])
    )

def get_arr_from_point(point):
    """
    Utility function converts `Point` structured data into `Dict` data.

    Example:
    INPUT: Point(42.983611, 81.249722)
    OUTPUT: [42.983611, -81.249722]
    """
    try:
        lat = point.x
        lng = point.y
        return [lat, lng]
    except Exception as e:
        return None


def get_polygon_from_multi_arr(arr):
    """
    Utility function converts multi-dimensial `array` structured data into
    `Polygon` data.

    Example:
    INPUT: [[42.989572, -81.23488], [42.976001, -81.233335], [42.97776, -81.208265], [42.989572, -81.23488]]
    OUTPUT: Polygon( ((42.99711 -81.275747, 42.975624 -81.30459500000001, 42.969088 -81.30116, 42.966826 -81.26733299999999, 42.971476 -81.22938499999999, 42.988064 -81.1947, 43.000628 -81.222002, 42.99711 -81.275747))
    """
    lines = []
    for coord in arr:
        lines.append( (coord[0],coord[1]) )
    return Polygon(lines)


def get_multi_arr_from_polygon(polygon):
    """
    Utility function converts multi-dimensial `array` structured data into
    `Polygon` data.

    Example:
    INPUT: Polygon( ((42.99711 -81.275747, 42.975624 -81.30459500000001, 42.969088 -81.30116, 42.966826 -81.26733299999999, 42.971476 -81.22938499999999, 42.988064 -81.1947, 43.000628 -81.222002, 42.99711 -81.275747))
    OUTPUT: [[42.989572, -81.23488], [42.976001, -81.233335], [42.97776, -81.208265], [42.989572, -81.23488]]
    """
    points_arr = []
    for linear_ring in polygon:
        linear_ring_tupile = linear_ring.array
        for line_point in linear_ring_tupile:
            points_arr.append([
                line_point[0],
                line_point[1]
            ])
    return [points_arr]
