from rest_framework import pagination


class AddressPagination(pagination.PageNumberPagination):
    page_size = 100
