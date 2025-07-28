import re

from django.db import transaction
from django.db.models import Q

from .models import Approval, ApprovalChain, StatusChoices


def apply_string_operator(requisition_value, rule_operator, rule_value):
    match rule_operator:
        case "exact":
            if requisition_value not in rule_value:
                return False
        case "iexact":
            if requisition_value.lower() not in [val.lower() for val in rule_value]:
                return False
        case "contains":
            if not any(val in requisition_value for val in rule_value):
                return False
        case "icontains":
            if not any(val.lower() in requisition_value.lower() for val in rule_value):
                return False
        case "startswith":
            if not any(requisition_value.startswith(val) for val in rule_value):
                return False
        case "istartswith":
            if not any(requisition_value.lower().startswith(val.lower()) for val in rule_value):
                return False
        case "endswith":
            if not any(requisition_value.endswith(val) for val in rule_value):
                return False
        case "iendswith":
            if not any(requisition_value.lower().endswith(val.lower()) for val in rule_value):
                return False
        case "is_null":
            if requisition_value not in (None, ""):
                return False
        case "regex":
            if not any(re.search(val, requisition_value) for val in rule_value):
                return False
        case _:
            return False

    return True


def rule_matching(rule, requisition):  # noqa: PLR0911
    match rule.field:
        case "external_reference":
            return apply_string_operator(requisition.external_reference, rule.operator, rule.value)
        case "owner":
            return apply_string_operator(requisition.owner.username, rule.operator, rule.value)
        case "owner_first_name":
            return apply_string_operator(requisition.owner.first_name, rule.operator, rule.value)
        case "owner_last_name":
            return apply_string_operator(requisition.owner.last_name, rule.operator, rule.value)
        case "owner_email":
            return apply_string_operator(requisition.owner.email, rule.operator, rule.value)
        case "project":
            return apply_string_operator(requisition.project.name, rule.operator, rule.value)
        case "project_code":
            return apply_string_operator(requisition.project.code, rule.operator, rule.value)
        case "project_description":
            return apply_string_operator(requisition.project.description, rule.operator, rule.value)
        case "supplier":
            return apply_string_operator(requisition.supplier, rule.operator, rule.value)
        case "currency":
            return apply_string_operator(requisition.currency, rule.operator, rule.value)
        case _:
            return False

    return True


@transaction.atomic
def generate_approvals(requisition):
    approvals = []

    approval_chains = (
        ApprovalChain.objects.filter(min_amount__lte=requisition.total_amount)
        .filter(Q(max_amount__gte=requisition.total_amount) | Q(max_amount__isnull=True))
        .filter(active=True)
        .order_by("sequence_number")
    )

    for approval_chain in approval_chains:
        rules = approval_chain.rules.all()  # type: ignore

        if all(rule_matching(rule, requisition) for rule in rules):
            approval = Approval(
                requisition=requisition,
                approver=approval_chain.approver,
                sequence_number=approval_chain.sequence_number,
                status=StatusChoices.PENDING,
            )

            approvals.append(approval)

    Approval.objects.bulk_create(approvals)
