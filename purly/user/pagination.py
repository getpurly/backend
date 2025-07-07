from rest_framework import pagination


class UserPagination(pagination.PageNumberPagination):
    page_size_query_param = "page_size"
    page_size = 100
    max_page_size = 100
