USER_FILTER_FIELDS = {
    "id": ["exact", "in"],
    "username": ["exact", "contains", "startswith", "endswith", "in", "regex"],
    "first_name": ["exact", "contains", "startswith", "endswith", "in", "regex"],
    "last_name": ["exact", "contains", "startswith", "endswith", "in", "regex"],
    "email": ["exact", "contains", "startswith", "endswith", "in", "regex"],
    "is_active": ["exact"],
    "date_joined": ["exact", "gt", "gte", "lt", "lte", "range"],
}
