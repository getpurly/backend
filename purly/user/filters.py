USER_STRING_REQUIRED = [
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

USER_STRING_OPTIONAL = [
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

USER_DATE = [
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

USER_FILTER_FIELDS = {
    "id": ["exact", "in"],
    "username": USER_STRING_REQUIRED,
    "first_name": USER_STRING_OPTIONAL,
    "last_name": USER_STRING_OPTIONAL,
    "email": USER_STRING_OPTIONAL,
    "is_active": ["exact"],
    "date_joined": USER_DATE,
}
