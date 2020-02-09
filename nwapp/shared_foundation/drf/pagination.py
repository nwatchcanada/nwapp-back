from rest_framework.pagination import PageNumberPagination


class NWAppResultsSetPagination(PageNumberPagination):
    """
    Default paginator class specific to our app
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 10000
