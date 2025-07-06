from rest_framework import pagination


class RequisitionPagination(pagination.PageNumberPagination):
    page_size = 100


class RequisitionLinePagination(pagination.PageNumberPagination):
    page_size = 100
