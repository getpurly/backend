from config.pagination import CustomPagination


class ApprovalPagination(CustomPagination):
    page_size_query_param = "page_size"
    page_size = 100
    max_page_size = 100
