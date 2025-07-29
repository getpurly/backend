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


def header_rule_matching(rule, requisition):
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


def line_rule_matching(rule, line):
    match rule.field:
        case "line_type":
            return apply_string_operator(line.line_type, rule.operator, rule.value)
        case "description":
            return apply_string_operator(line.description, rule.operator, rule.value)
        case "category":
            return apply_string_operator(line.category, rule.operator, rule.value)
        case "manufacturer":
            return apply_string_operator(line.manufacturer, rule.operator, rule.value)
        case "manufacturer_part_number":
            return apply_string_operator(line.manufacturer_part_number, rule.operator, rule.value)
        case "uom":
            return apply_string_operator(line.uom, rule.operator, rule.value)
        case "payment_term":
            return apply_string_operator(line.payment_term, rule.operator, rule.value)
        case "ship_to_name":
            return apply_string_operator(line.ship_to_name, rule.operator, rule.value)
        case "ship_to_code":
            return apply_string_operator(line.ship_to_code, rule.operator, rule.value)
        case "ship_to_attention":
            return apply_string_operator(line.ship_to_attention, rule.operator, rule.value)
        case "ship_to_phone":
            return apply_string_operator(line.ship_to_phone, rule.operator, rule.value)
        case "ship_to_street1":
            return apply_string_operator(line.ship_to_street1, rule.operator, rule.value)
        case "ship_to_street2":
            return apply_string_operator(line.ship_to_street2, rule.operator, rule.value)
        case "ship_to_city":
            return apply_string_operator(line.ship_to_city, rule.operator, rule.value)
        case "ship_to_state":
            return apply_string_operator(line.ship_to_state, rule.operator, rule.value)
        case "ship_to_zip":
            return apply_string_operator(line.ship_to_zip, rule.operator, rule.value)
        case "ship_to_country":
            return apply_string_operator(line.ship_to_country, rule.operator, rule.value)
        case _:
            return False


@transaction.atomic
def generate_approvals(requisition):
    approvals = []

    approval_chains = (
        ApprovalChain.objects.filter(min_amount__lte=requisition.total_amount)
        .filter(Q(max_amount__gte=requisition.total_amount) | Q(max_amount__isnull=True))
        .filter(active=True)
        .filter(deleted=False)
        .order_by("sequence_number")
    )

    for approval_chain in approval_chains:
        header_rules = approval_chain.approval_chain_header_rules.all()  # type: ignore
        line_rules = approval_chain.approval_chain_line_rules.all()  # type: ignore

        if not all(header_rule_matching(rule, requisition) for rule in header_rules):
            continue

        for rule in line_rules:
            match_mode = rule.match_mode
            lines = requisition.lines.all()

            match match_mode:
                case "all":
                    if not all(line_rule_matching(rule, line) for line in lines):
                        break
                case _:
                    if not any(line_rule_matching(rule, line) for line in lines):
                        break

        else:
            approval = Approval(
                requisition=requisition,
                approver=approval_chain.approver,
                sequence_number=approval_chain.sequence_number,
                status=StatusChoices.PENDING,
            )

            approvals.append(approval)

    Approval.objects.bulk_create(approvals)
