from config.pagination import CustomPagination


class RequisitionPagination(CustomPagination):
    page_size = 50


class RequisitionLinePagination(CustomPagination):
    page_size = 50
