from django.http import JsonResponse


def get_version_api(request):
    """
    Function returns basic information about our project.
    """
    data = {
        'name': 'NWApp API Web-Service',
        'version': 1.0,
    }
    return JsonResponse(data)
