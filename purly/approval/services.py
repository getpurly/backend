import re
from decimal import Decimal

from django.db import transaction
from django.db.models import Min, Q
from django.utils import timezone
from rest_framework import exceptions

from config.exceptions import BadRequest
from purly.requisition.models import RequisitionStatusChoices

from .emails import send_approval_email, send_fully_approved_email, send_reject_email
from .models import (
    Approval,
    ApprovalChain,
    ApprovalChainModeChoices,
    ApprovalStatusChoices,
    HeaderFieldStringChoices,
    LineFieldNumberChoices,
    LineFieldStringChoices,
    LineMatchModeChoices,
    LookupNumberChoices,
    LookupStringChoices,
)


def perform_lookup(value, rule_lookup, rule_value):  # noqa: C901 PLR0911 PLR0912
    if rule_lookup != LookupStringChoices.IS_NULL and value is None:
        return False

    match rule_lookup:
        case LookupStringChoices.EXACT:
            if value not in rule_value:
                return False
        case LookupStringChoices.IEXACT:
            if not isinstance(value, str):
                return False
            if value.lower() not in [val.lower() for val in rule_value]:
                return False
        case LookupStringChoices.CONTAINS:
            if not any(val in value for val in rule_value):
                return False
        case LookupStringChoices.ICONTAINS:
            if not isinstance(value, str):
                return False
            if not any(val.lower() in value.lower() for val in rule_value):
                return False
        case LookupStringChoices.STARTS_WITH:
            if not any(value.startswith(val) for val in rule_value):
                return False
        case LookupStringChoices.ISTARTS_WITH:
            if not isinstance(value, str):
                return False
            if not any(value.lower().startswith(val.lower()) for val in rule_value):
                return False
        case LookupStringChoices.ENDS_WITH:
            if not any(value.endswith(val) for val in rule_value):
                return False
        case LookupStringChoices.IENDS_WITH:
            if not isinstance(value, str):
                return False
            if not any(value.lower().endswith(val.lower()) for val in rule_value):
                return False
        case LookupStringChoices.REGEX:
            if not any(re.search(val, value) for val in rule_value):
                return False
        case LookupStringChoices.IS_NULL:
            if value not in (None, ""):
                return False
        case LookupNumberChoices.EQUAL:
            if value != Decimal(rule_value[0]):
                return False
        case LookupNumberChoices.NOT_EQUAL:
            if value == Decimal(rule_value[0]):
                return False
        case LookupNumberChoices.GT:
            if not value > Decimal(rule_value[0]):
                return False
        case LookupNumberChoices.GTE:
            if not value >= Decimal(rule_value[0]):
                return False
        case LookupNumberChoices.LT:
            if not value < Decimal(rule_value[0]):
                return False
        case LookupNumberChoices.LTE:
            if not value <= Decimal(rule_value[0]):
                return False
        case _:
            raise ValueError(f"Unsupported rule_lookup: {rule_lookup}")

    return True


def header_rule_matching(requisition, rule):
    field_map = {
        HeaderFieldStringChoices.CURRENCY: requisition.currency,
        HeaderFieldStringChoices.EXTERNAL_REFERENCE: requisition.external_reference,
        HeaderFieldStringChoices.JUSTIFICATION: requisition.justification,
        HeaderFieldStringChoices.NAME: requisition.name,
        HeaderFieldStringChoices.OWNER: requisition.owner.username,
        HeaderFieldStringChoices.OWNER_EMAIL: requisition.owner.email,
        HeaderFieldStringChoices.OWNER_FIRST_NAME: requisition.owner.first_name,
        HeaderFieldStringChoices.OWNER_LAST_NAME: requisition.owner.last_name,
        HeaderFieldStringChoices.PROJECT_NAME: requisition.project.name
        if requisition.project
        else None,
        HeaderFieldStringChoices.PROJECT_CODE: requisition.project.project_code
        if requisition.project
        else None,
        HeaderFieldStringChoices.PROJECT_DESCRIPTION: requisition.project.description
        if requisition.project
        else None,
        HeaderFieldStringChoices.SUPPLIER: requisition.supplier,
    }

    header_value = field_map.get(rule.field)

    return perform_lookup(header_value, rule.lookup, rule.value)


def line_rule_matching(line, rule):
    field_map = {
        LineFieldStringChoices.CATEGORY: line.category,
        LineFieldStringChoices.DESCRIPTION: line.description,
        LineFieldNumberChoices.LINE_TOTAL: line.line_total,
        LineFieldStringChoices.MANUFACTURER: line.manufacturer,
        LineFieldStringChoices.MANUFACTURER_PART_NUMBER: line.manufacturer_part_number,
        LineFieldStringChoices.PAYMENT_TERM: line.payment_term,
        LineFieldStringChoices.SHIP_TO_ATTENTION: line.ship_to.attention,
        LineFieldStringChoices.SHIP_TO_CITY: line.ship_to.city,
        LineFieldStringChoices.SHIP_TO_CODE: line.ship_to.address_code,
        LineFieldStringChoices.SHIP_TO_COUNTRY: line.ship_to.country,
        LineFieldStringChoices.SHIP_TO_DELIVERY_INSTRUCTIONS: line.ship_to.delivery_instructions,
        LineFieldStringChoices.SHIP_TO_DESCRIPTION: line.ship_to.description,
        LineFieldStringChoices.SHIP_TO_NAME: line.ship_to.name,
        LineFieldStringChoices.SHIP_TO_PHONE: line.ship_to.phone,
        LineFieldStringChoices.SHIP_TO_STATE: line.ship_to.state,
        LineFieldStringChoices.SHIP_TO_STREET1: line.ship_to.street1,
        LineFieldStringChoices.SHIP_TO_STREET2: line.ship_to.street2,
        LineFieldStringChoices.SHIP_TO_ZIP_CODE: line.ship_to.zip_code,
        LineFieldStringChoices.UNIT_OF_MEASURE: line.unit_of_measure,
        LineFieldNumberChoices.UNIT_PRICE: line.unit_price,
    }

    line_value = field_map.get(rule.field)

    return perform_lookup(line_value, rule.lookup, rule.value)


def fetch_trigger_metadata(approval_chain, header_rules, line_rules):
    header_rules_metadata = []
    line_rules_metadata = []

    for rule in header_rules:
        header_rule = {"field": rule.field, "lookup": rule.lookup, "value": rule.value}

        header_rules_metadata.append(header_rule)

    for rule in line_rules:
        line_rule = {
            "match_mode": rule.match_mode,
            "field": rule.field,
            "lookup": rule.lookup,
            "value": rule.value,
        }

        line_rules_metadata.append(line_rule)

    approver_data = None

    if approval_chain.approver:
        approver_data = {
            "id": approval_chain.approver.id,
            "username": approval_chain.approver.username,
        }

    approver_group_data = None

    if approval_chain.approver_group:
        approver_group_data = {
            "id": approval_chain.approver_group.id,
            "name": approval_chain.approver_group.name,
        }

    return {
        "id": approval_chain.id,
        "name": approval_chain.name,
        "approver_mode": approval_chain.approver_mode,
        "approver": approver_data,
        "approver_group": approver_group_data,
        "sequence_number": approval_chain.sequence_number,
        "min_amount": str(Decimal(approval_chain.min_amount)),
        "max_amount": str(Decimal(approval_chain.max_amount))
        if approval_chain.max_amount
        else None,
        "header_rules": header_rules_metadata,
        "line_rules": line_rules_metadata,
    }


def generate_approvals(requisition):
    lines = requisition.lines.all()

    approvals = []

    approval_chains = (
        ApprovalChain.objects_active.filter(min_amount__lte=requisition.total_amount)
        .filter(Q(max_amount__gte=requisition.total_amount) | Q(max_amount__isnull=True))
        .filter(active=True)
        .order_by("sequence_number")
        .prefetch_related(
            "approval_chain_header_rules", "approval_chain_line_rules", "approver_group__approver"
        )
    )

    if not approval_chains.exists():
        return False

    for approval_chain in approval_chains:
        header_rules = approval_chain.approval_chain_header_rules.all()  # type: ignore
        line_rules = approval_chain.approval_chain_line_rules.all()  # type: ignore

        if not all(header_rule_matching(requisition, rule) for rule in header_rules):
            continue

        for rule in line_rules:
            match rule.match_mode:
                case LineMatchModeChoices.ALL:
                    if not all(line_rule_matching(line, rule) for line in lines):
                        break
                case _:
                    if not any(line_rule_matching(line, rule) for line in lines):
                        break

        else:
            rule_metadata = fetch_trigger_metadata(approval_chain, header_rules, line_rules)

            if approval_chain.approver_mode == ApprovalChainModeChoices.INDIVIDUAL:
                approval = Approval(
                    requisition=requisition,
                    approver=approval_chain.approver,
                    sequence_number=approval_chain.sequence_number,
                    rule_metadata=rule_metadata,
                    status=ApprovalStatusChoices.PENDING,
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
                        rule_metadata=rule_metadata,
                        status=ApprovalStatusChoices.PENDING,
                        system_generated=True,
                    )

                    approvals.append(approval)

    Approval.objects.bulk_create(approvals)

    return True


def cancel_approvals(requisition):
    approvals = []

    timestamp = timezone.now()

    for approval in requisition.approvals.filter(status=ApprovalStatusChoices.PENDING):
        approval.status = ApprovalStatusChoices.CANCELLED
        approval.updated_at = timestamp

        approvals.append(approval)

    Approval.objects.bulk_update(approvals, ["status", "updated_at"])


def on_reject(approval, requisition):
    cancel_approvals(requisition)

    requisition.status = RequisitionStatusChoices.DRAFT
    requisition.rejected_at = timezone.now()

    requisition.save()

    send_reject_email(approval, requisition)


@transaction.atomic
def on_fully_approved(requisition):
    if (
        retrieve_sequence_min(requisition) is None
        and requisition.status == RequisitionStatusChoices.PENDING_APPROVAL
        and requisition.approved_at is None
    ):
        requisition.status = RequisitionStatusChoices.APPROVED
        requisition.approved_at = timezone.now()

        requisition.save()

        send_fully_approved_email(requisition)


def retrieve_sequence_min(requisition):
    value = Approval.objects_active.filter(
        requisition=requisition, status=ApprovalStatusChoices.PENDING
    ).aggregate(Min("sequence_number"))

    return value["sequence_number__min"]


def check_if_current_approver(approval):
    sequence_min_value = retrieve_sequence_min(approval.requisition)

    return approval.sequence_number == sequence_min_value


def approval_request_validation(request_user, action, approval):
    if approval.approver != request_user:
        raise exceptions.PermissionDenied(f"You cannot {action} on someone else's behalf.")

    if (
        check_if_current_approver(approval) is False
        and approval.status == ApprovalStatusChoices.PENDING
    ):
        raise BadRequest(detail="An earlier approval is still pending.")

    if action == "approve":
        if approval.status == ApprovalStatusChoices.APPROVED:
            raise BadRequest(detail="This approval has already been approved.")
        if approval.status != ApprovalStatusChoices.PENDING:
            raise BadRequest(detail="This approval must be in pending status to approve.")
    else:
        if approval.status == ApprovalStatusChoices.REJECTED:
            raise BadRequest(detail="This approval has already been rejected.")
        if approval.status != ApprovalStatusChoices.PENDING:
            raise BadRequest(detail="This approval must be in pending status to reject.")


@transaction.atomic
def notify_current_sequence(requisition):
    sequence_min_value = retrieve_sequence_min(requisition)

    if sequence_min_value is not None:
        timestamp = timezone.now()

        for approval in requisition.approvals.filter(
            sequence_number=sequence_min_value,
            status=ApprovalStatusChoices.PENDING,
            notified_at=None,
            deleted=False,
        ).select_related("approver"):
            approval.notified_at = timestamp
            approval.updated_at = timestamp

            approval.save()

            send_approval_email(requisition, approval)
