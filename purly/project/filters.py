PROJECT_STRING_REQUIRED = [
    "exact",
    "iexact",
    "contains",
    "icontains",
    "startswith",
    "istartswith",
    "endswith",
    "iendswith",
    "in",
    "regex",
]

PROJECT_STRING_OPTIONAL = [
    "exact",
    "iexact",
    "contains",
    "icontains",
    "startswith",
    "istartswith",
    "endswith",
    "iendswith",
    "in",
    "regex",
    "isnull",
]

PROJECT_START_END_DATE = [
    "exact",
    "gt",
    "gte",
    "lt",
    "lte",
    "range",
    "year",
    "quarter",
    "month",
    "week",
    "week_day",
    "day",
    "isnull",
]

PROJECT_DATE = [
    "exact",
    "gt",
    "gte",
    "lt",
    "lte",
    "date",
    "range",
    "year",
    "quarter",
    "month",
    "week",
    "week_day",
    "day",
]

PROJECT_FILTER_FIELDS = {
    "id": ["exact", "in"],
    "name": PROJECT_STRING_REQUIRED,
    "project_code": PROJECT_STRING_OPTIONAL,
    "description": PROJECT_STRING_REQUIRED,
    "start_date": PROJECT_START_END_DATE,
    "end_date": PROJECT_START_END_DATE,
    "created_at": PROJECT_DATE,
    "created_by__username": PROJECT_STRING_REQUIRED,
    "updated_at": PROJECT_DATE,
    "updated_by__username": PROJECT_STRING_REQUIRED,
}
