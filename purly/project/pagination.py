from rest_framework import pagination


class ProjectPagination(pagination.PageNumberPagination):
    page_size = 100
