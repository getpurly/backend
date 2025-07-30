import re

from django.db import transaction
from django.db.models import Q

from .models import (
    Approval,
    ApprovalChain,
    ApprovalChainModeChoices,
    LineMatchModeChoices,
    OperatorChoices,
    StatusChoices,
)


def check_string_operator(requisition_value, rule_operator, rule_value):
    match rule_operator:
        case OperatorChoices.EXACT:
            if requisition_value not in rule_value:
                return False
        case OperatorChoices.IEXACT:
            if requisition_value.lower() not in [val.lower() for val in rule_value]:
                return False
        case OperatorChoices.CONTAINS:
            if not any(val in requisition_value for val in rule_value):
                return False
        case OperatorChoices.ICONTAINS:
            if not any(val.lower() in requisition_value.lower() for val in rule_value):
                return False
        case OperatorChoices.STARTS_WITH:
            if not any(requisition_value.startswith(val) for val in rule_value):
                return False
        case OperatorChoices.ISTARTS_WITH:
            if not any(requisition_value.lower().startswith(val.lower()) for val in rule_value):
                return False
        case OperatorChoices.ENDS_WITH:
            if not any(requisition_value.endswith(val) for val in rule_value):
                return False
        case OperatorChoices.IENDS_WITH:
            if not any(requisition_value.lower().endswith(val.lower()) for val in rule_value):
                return False
        case OperatorChoices.REGEX:
            if not any(re.search(val, requisition_value) for val in rule_value):
                return False
        case OperatorChoices.IS_NULL:
            if requisition_value not in (None, ""):
                return False
        case _:
            return False

    return True


def rule_matching(obj, rule):
    value = getattr(obj, rule.field)

    return check_string_operator(value, rule.operator, rule.value)


@transaction.atomic
def generate_approvals(requisition):
    lines = requisition.lines.all()

    approvals = []

    approval_chains = (
        ApprovalChain.objects.filter(min_amount__lte=requisition.total_amount)
        .filter(Q(max_amount__gte=requisition.total_amount) | Q(max_amount__isnull=True))
        .filter(active=True)
        .filter(deleted=False)
        .order_by("sequence_number")
        .prefetch_related(
            "approval_chain_header_rules", "approval_chain_line_rules", "approver_group__approver"
        )
    )

    for approval_chain in approval_chains:
        header_rules = approval_chain.approval_chain_header_rules.all()  # type: ignore
        line_rules = approval_chain.approval_chain_line_rules.all()  # type: ignore

        if not all(rule_matching(requisition, rule) for rule in header_rules):
            continue

        for rule in line_rules:
            match rule.match_mode:
                case LineMatchModeChoices.ALL:
                    if not all(rule_matching(line, rule) for line in lines):
                        break
                case _:
                    if not any(rule_matching(line, rule) for line in lines):
                        break

        else:
            if approval_chain.approver_mode == ApprovalChainModeChoices.INDIVIDUAL:
                approval = Approval(
                    requisition=requisition,
                    approver=approval_chain.approver,
                    sequence_number=approval_chain.sequence_number,
                    status=StatusChoices.PENDING,
                )

                approvals.append(approval)
            else:
                approvers = approval_chain.approver_group.approver.all()  # type: ignore

                for approver in approvers:
                    approval = Approval(
                        requisition=requisition,
                        approver=approver,
                        sequence_number=approval_chain.sequence_number,
                        status=StatusChoices.PENDING,
                    )

                    approvals.append(approval)

    Approval.objects.bulk_create(approvals)
