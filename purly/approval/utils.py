import re
from decimal import Decimal

from django.db import transaction
from django.db.models import Q

from .models import (
    Approval,
    ApprovalChain,
    ApprovalChainModeChoices,
    LineMatchModeChoices,
    LookupNumberChoices,
    LookupStringChoices,
    StatusChoices,
)


def perform_lookup(requisition_value, rule_lookup, rule_value):
    if rule_lookup != LookupStringChoices.IS_NULL and requisition_value is None:
        return False

    match rule_lookup:
        case LookupStringChoices.EXACT:
            if requisition_value not in rule_value:
                return False
        case LookupStringChoices.IEXACT:
            if not isinstance(requisition_value, str):
                return False
            if requisition_value.lower() not in [val.lower() for val in rule_value]:
                return False
        case LookupStringChoices.CONTAINS:
            if not any(val in requisition_value for val in rule_value):
                return False
        case LookupStringChoices.ICONTAINS:
            if not isinstance(requisition_value, str):
                return False
            if not any(val.lower() in requisition_value.lower() for val in rule_value):
                return False
        case LookupStringChoices.STARTS_WITH:
            if not any(requisition_value.startswith(val) for val in rule_value):
                return False
        case LookupStringChoices.ISTARTS_WITH:
            if not isinstance(requisition_value, str):
                return False
            if not any(requisition_value.lower().startswith(val.lower()) for val in rule_value):
                return False
        case LookupStringChoices.ENDS_WITH:
            if not any(requisition_value.endswith(val) for val in rule_value):
                return False
        case LookupStringChoices.IENDS_WITH:
            if not isinstance(requisition_value, str):
                return False
            if not any(requisition_value.lower().endswith(val.lower()) for val in rule_value):
                return False
        case LookupStringChoices.REGEX:
            if not any(re.search(val, requisition_value) for val in rule_value):
                return False
        case LookupStringChoices.IS_NULL:
            if requisition_value not in (None, ""):
                return False
        case LookupNumberChoices.EQUAL:
            if requisition_value != Decimal(rule_value[0]):
                return False
        case LookupNumberChoices.NOT_EQUAL:
            if requisition_value == Decimal(rule_value[0]):
                return False
        case LookupNumberChoices.GT:
            if not requisition_value > Decimal(rule_value[0]):
                return False
        case LookupNumberChoices.GTE:
            if not requisition_value >= Decimal(rule_value[0]):
                return False
        case LookupNumberChoices.LT:
            if not requisition_value < Decimal(rule_value[0]):
                return False
        case LookupNumberChoices.LTE:
            if not requisition_value <= Decimal(rule_value[0]):
                return False
        case _:
            raise ValueError(f"Unsupported rule_lookup: {rule_lookup}")

    return True


def rule_matching(obj, rule):
    value = getattr(obj, rule.field, None)

    return perform_lookup(value, rule.lookup, rule.value)


def create_snapshot_data(approval_chain, header_rules, line_rules):
    snapshot_header_rules = []
    snapshot_line_rules = []

    for rule in header_rules:
        header_rule = {"field": rule.field, "lookup": rule.lookup, "value": rule.value}

        snapshot_header_rules.append(header_rule)

    for rule in line_rules:
        line_rule = {
            "match_mode": rule.match_mode,
            "field": rule.field,
            "lookup": rule.lookup,
            "value": rule.value,
        }

        snapshot_line_rules.append(line_rule)

    approver_data = None

    if approval_chain.approver:
        approver_data = {
            "id": approval_chain.approver.id,
            "username": str(approval_chain.approver.username),
        }

    approver_group_data = None

    if approval_chain.approver_group:
        approver_group_data = {
            "id": approval_chain.approver_group.id,
            "name": str(approval_chain.approver_group.name),
        }

    return {
        "id": approval_chain.id,
        "name": approval_chain.name,
        "approver_mode": approval_chain.approver_mode,
        "approver": approver_data,
        "approver_group": approver_group_data,
        "sequence_number": approval_chain.sequence_number,
        "min_amount": float(approval_chain.min_amount),
        "max_amount": float(approval_chain.max_amount) if approval_chain.max_amount else None,
        "header_rules": snapshot_header_rules,
        "line_rules": snapshot_line_rules,
    }


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
            snapshot_data = create_snapshot_data(approval_chain, header_rules, line_rules)

            if approval_chain.approver_mode == ApprovalChainModeChoices.INDIVIDUAL:
                approval = Approval(
                    requisition=requisition,
                    approver=approval_chain.approver,
                    sequence_number=approval_chain.sequence_number,
                    snapshot_data=snapshot_data,
                    status=StatusChoices.PENDING,
                    system_generated=True,
                )

                approvals.append(approval)
            else:
                approvers = approval_chain.approver_group.approver.all()  # type: ignore

                for approver in approvers:
                    approval = Approval(
                        requisition=requisition,
                        approver=approver,
                        sequence_number=approval_chain.sequence_number,
                        snapshot_data=snapshot_data,
                        status=StatusChoices.PENDING,
                        system_generated=True,
                    )

                    approvals.append(approval)

    Approval.objects.bulk_create(approvals)
