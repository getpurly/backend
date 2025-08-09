REQUISITION_STRING_REQUIRED = [
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

REQUISITION_STRING_OPTIONAL = [
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

REQUISITION_NUMBER = ["exact", "gt", "gte", "lt", "lte", "in", "range"]

REQUISITION_NEED_BY_DATE = [
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

REQUISITION_DATE = [
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

REQUISITION_FILTER_FIELDS = {
    "id": ["exact", "in"],
    "name": REQUISITION_STRING_REQUIRED,
    "external_reference": REQUISITION_STRING_OPTIONAL,
    "status": REQUISITION_STRING_REQUIRED,
    "owner__username": REQUISITION_STRING_REQUIRED,
    "project__name": REQUISITION_STRING_OPTIONAL,
    "supplier": REQUISITION_STRING_REQUIRED,
    "justification": REQUISITION_STRING_REQUIRED,
    "total_amount": REQUISITION_NUMBER,
    "currency": REQUISITION_STRING_REQUIRED,
    "created_at": REQUISITION_DATE,
    "created_by__username": REQUISITION_STRING_REQUIRED,
    "updated_at": REQUISITION_DATE,
    "updated_by__username": REQUISITION_STRING_REQUIRED,
    "submitted_at": [*REQUISITION_DATE, "isnull"],
    "approved_at": [*REQUISITION_DATE, "isnull"],
    "rejected_at": [*REQUISITION_DATE, "isnull"],
}


REQUISITION_LINE_FILTER_FIELDS = {
    "id": ["exact", "in"],
    "line_number": REQUISITION_NUMBER,
    "line_type": REQUISITION_STRING_REQUIRED,
    "description": REQUISITION_STRING_REQUIRED,
    "category": REQUISITION_STRING_REQUIRED,
    "manufacturer": REQUISITION_STRING_OPTIONAL,
    "manufacturer_part_number": REQUISITION_STRING_OPTIONAL,
    "quantity": REQUISITION_NUMBER,
    "unit_of_measure": REQUISITION_STRING_OPTIONAL,
    "unit_price": REQUISITION_NUMBER,
    "line_total": REQUISITION_NUMBER,
    "payment_term": REQUISITION_STRING_REQUIRED,
    "need_by": REQUISITION_NEED_BY_DATE,
    "requisition__id": REQUISITION_NUMBER,
    "ship_to__name": REQUISITION_STRING_REQUIRED,
    "created_at": REQUISITION_DATE,
    "created_by__username": REQUISITION_STRING_REQUIRED,
    "updated_at": REQUISITION_DATE,
    "updated_by__username": REQUISITION_STRING_REQUIRED,
}
