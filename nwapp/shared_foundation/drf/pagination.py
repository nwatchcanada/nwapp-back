from rest_framework.pagination import PageNumberPagination


class TinyResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 10000


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 250
    page_size_query_param = 'page_size'
    max_page_size = 10000
