PROJECT_FILTER_FIELDS = {
    "id": ["exact", "in"],
    "name": ["exact", "contains", "startswith", "endswith", "in", "regex"],
    "project_code": ["exact", "contains", "startswith", "endswith", "in", "regex", "isnull"],
    "description": ["exact", "contains", "startswith", "endswith", "in", "regex"],
    "start_date": ["exact", "gt", "gte", "lt", "lte", "range", "isnull"],
    "end_date": ["exact", "gt", "gte", "lt", "lte", "range", "isnull"],
    "created_at": ["exact", "gt", "gte", "lt", "lte", "range"],
    "created_by__username": ["exact", "contains", "startswith", "endswith", "in", "regex"],
    "updated_at": ["exact", "gt", "gte", "lt", "lte", "range"],
    "updated_by__username": [
        "exact",
        "contains",
        "startswith",
        "endswith",
        "in",
        "regex",
    ],
}
