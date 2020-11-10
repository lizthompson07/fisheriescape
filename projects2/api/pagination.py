from rest_framework.pagination import PageNumberPagination


class SmallSetPagination(PageNumberPagination):
    page_size = 10


class PaginationBy100(PageNumberPagination):
    page_size = 100
