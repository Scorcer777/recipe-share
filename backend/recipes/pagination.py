from rest_framework.pagination import PageNumberPagination

from foodgram_project.settings import PAGE_SIZE


class CustomPagination(PageNumberPagination):
    page_size = PAGE_SIZE
    page_query_param = 'page'
    page_size_query_param = 'limit'
