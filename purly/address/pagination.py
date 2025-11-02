from config.pagination import CustomPagination


class AddressPagination(CustomPagination):
    page_size_query_param = "page_size"
    page_size = 100
    max_page_size = 100
