import re
from decimal import Decimal

from django.db import transaction
from django.db.models import Max, Min, Q
from django.utils import timezone
from rest_framework import exceptions

from config.exceptions import BadRequest
from purly.requisition.models import Requisition, RequisitionStatusChoices
from purly.requisition.services import on_reject_requisition

from .emails import send_approval_email, send_fully_approved_email
from .models import (
    Approval,
    ApprovalChain,
    ApprovalChainModeChoices,
    ApprovalStatusChoices,
    HeaderFieldStringChoices,
    LineFieldNumberChoices,
    LineFieldStringChoices,
    LookupNumberChoices,
    LookupStringChoices,
    MatchModeChoices,
    OperatorChoices,
)


def perform_lookup(value, rule_lookup, rule_value):  # noqa: PLR0911, PLR0912
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
            if not isinstance(value, str):
                return False
            if not any(value.startswith(val) for val in rule_value):
                return False
        case LookupStringChoices.ISTARTS_WITH:
            if not isinstance(value, str):
                return False
            if not any(value.lower().startswith(val.lower()) for val in rule_value):
                return False
        case LookupStringChoices.ENDS_WITH:
            if not isinstance(value, str):
                return False
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
            return False

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


def fetch_rule_metadata(approval_chain, header_rules, line_rules):
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
            "group_mode": approval_chain.group_mode,
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
        "header_rule_logic": approval_chain.header_rule_logic,
        "line_rule_logic": approval_chain.line_rule_logic,
        "cross_rule_logic": approval_chain.cross_rule_logic,
        "valid_from": str(approval_chain.valid_from) if approval_chain.valid_from else None,
        "valid_to": str(approval_chain.valid_to) if approval_chain.valid_to else None,
        "header_rules": header_rules_metadata if len(header_rules_metadata) > 0 else None,
        "line_rules": line_rules_metadata if len(line_rules_metadata) > 0 else None,
    }


def header_check(requisition, approval_chain, header_rules):
    if len(header_rules) == 0:
        return True

    if approval_chain.header_rule_logic == OperatorChoices.AND:
        return all(header_rule_matching(requisition, rule) for rule in header_rules)

    if approval_chain.header_rule_logic == OperatorChoices.OR:
        return any(header_rule_matching(requisition, rule) for rule in header_rules)

    return False


def line_check(lines, approval_chain, line_rules):
    line_rule_results = []

    if len(line_rules) == 0:
        return True

    for rule in line_rules:
        if rule.match_mode == MatchModeChoices.ALL:
            result = all(line_rule_matching(line, rule) for line in lines)
        elif rule.match_mode == MatchModeChoices.ANY:
            result = any(line_rule_matching(line, rule) for line in lines)
        else:
            result = False

        line_rule_results.append(result)

    if approval_chain.line_rule_logic == OperatorChoices.AND:
        return all(line_rule_results)

    if approval_chain.line_rule_logic == OperatorChoices.OR:
        return any(line_rule_results)

    return False


def generate_approvals(requisition):
    approvals = []

    lines = list(requisition.lines.select_related("ship_to"))

    approval_chains = (
        ApprovalChain.objects.current()  # type: ignore
        .filter(min_amount__lte=requisition.total_amount)
        .filter(Q(max_amount__gte=requisition.total_amount) | Q(max_amount__isnull=True))
        .order_by("sequence_number")
        .select_related("approver", "approver_group")
        .prefetch_related(
            "approval_chain_header_rules", "approval_chain_line_rules", "approver_group__approver"
        )
    )

    for approval_chain in approval_chains:
        header_rules = approval_chain.approval_chain_header_rules.all()
        line_rules = approval_chain.approval_chain_line_rules.all()

        header_result = header_check(requisition, approval_chain, header_rules)
        line_result = line_check(lines, approval_chain, line_rules)

        if approval_chain.cross_rule_logic == OperatorChoices.AND:
            if not all([header_result, line_result]):
                continue
        elif not any([header_result, line_result]):
            continue

        rule_metadata = fetch_rule_metadata(approval_chain, header_rules, line_rules)

        if approval_chain.approver_mode == ApprovalChainModeChoices.INDIVIDUAL:
            if not approval_chain.approver.is_active:
                return (
                    False,
                    f"This requisition cannot be submitted because the approval chain {approval_chain} contains an inactive approver.",  # noqa: E501
                )

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
            approvers = approval_chain.approver_group.approver.filter(is_active=True)

            if len(approvers) == 0:
                return (
                    False,
                    f"This requisition cannot be submitted because the approval group {approval_chain.approver_group} contains no active approvers.",  # noqa: E501
                )

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

    if len(approvals) == 0:
        return (False, "This requisition cannot be submitted because no approval chains matched.")

    Approval.objects.bulk_create(approvals)

    return (True, "")


def cancel_approvals(requisition):
    approvals = []

    timestamp = timezone.now()

    for approval in requisition.approvals.filter(
        status=ApprovalStatusChoices.PENDING, deleted=False
    ):
        approval.status = ApprovalStatusChoices.CANCELLED
        approval.updated_at = timestamp

        approvals.append(approval)

    Approval.objects.bulk_update(approvals, ["status", "updated_at"])


@transaction.atomic
def cancel_user_approvals(user):
    approvals = []
    requisitions = set()

    timestamp = timezone.now()

    for approval in Approval.objects.active().filter(  # type: ignore
        status=ApprovalStatusChoices.PENDING, approver=user
    ):
        approval.status = ApprovalStatusChoices.CANCELLED
        approval.updated_at = timestamp

        approvals.append(approval)

        requisitions.add(approval.requisition_id)

    Approval.objects.bulk_update(approvals, ["status", "updated_at"])

    for requisition_id in requisitions:
        requisition = Requisition.objects.get(pk=requisition_id)

        transaction.on_commit(lambda requisition=requisition: notify_current_sequence(requisition))
        transaction.on_commit(lambda requisition=requisition: check_fully_approved(requisition))


def cancel_group_approvals(approval):
    approvals = []

    timestamp = timezone.now()

    for related_approval in Approval.objects.active().filter(  # type: ignore
        status=ApprovalStatusChoices.PENDING,
        requisition=approval.requisition,
        sequence_number=approval.sequence_number,
    ):
        related_approval.status = ApprovalStatusChoices.CANCELLED
        related_approval.updated_at = timestamp

        approvals.append(related_approval)

    Approval.objects.bulk_update(approvals, ["status", "updated_at"])


def bypass_approvals(requisition, request_user):
    approvals = []

    timestamp = timezone.now()

    for approval in requisition.approvals.filter(
        status=ApprovalStatusChoices.PENDING, deleted=False
    ):
        approval.status = ApprovalStatusChoices.SKIPPED
        approval.skipped_at = approval.updated_at = timestamp
        approval.updated_by = request_user

        approvals.append(approval)

    Approval.objects.bulk_update(approvals, ["status", "skipped_at", "updated_at", "updated_by"])

    transaction.on_commit(lambda: check_fully_approved(requisition))


def on_approve_skip(approval, requisition, action, **kwargs):
    if action == "approve":
        approval.status = ApprovalStatusChoices.APPROVED
        approval.approved_at = timezone.now()

    if action == "skip":
        approval.status = ApprovalStatusChoices.SKIPPED
        approval.skipped_at = timezone.now()

    request_user = kwargs.get("request_user")

    if request_user:
        approval.updated_by = request_user

    approval.save()

    if approval.rule_metadata is not None and approval.rule_metadata["approver_mode"] == "group":
        group_mode = approval.rule_metadata["approver_group"]["group_mode"]

        if group_mode == MatchModeChoices.ANY:
            cancel_group_approvals(approval)

    send_email = kwargs.get("send_email", True)

    if send_email:
        transaction.on_commit(lambda: notify_current_sequence(requisition))
        transaction.on_commit(lambda: check_fully_approved(requisition))

    return approval


def on_reject(approval, requisition, **kwargs):
    approval.status = ApprovalStatusChoices.REJECTED
    approval.rejected_at = timezone.now()

    request_user = kwargs.get("request_user")

    if request_user:
        approval.updated_by = request_user

    approval.save()

    cancel_approvals(requisition)

    update_requisition = kwargs.get("update_requisition", True)

    if update_requisition:
        on_reject_requisition(approval, requisition)

    return approval


def retrieve_sequence_min(requisition):
    value = (
        Approval.objects.active()  # type: ignore
        .filter(requisition=requisition, status=ApprovalStatusChoices.PENDING)
        .aggregate(Min("sequence_number"))
    )

    return value["sequence_number__min"]


def retrieve_sequence_max(requisition):
    value = (
        Approval.objects.active()  # type: ignore
        .filter(requisition=requisition, status=ApprovalStatusChoices.PENDING)
        .aggregate(Max("sequence_number"))
    )

    return value["sequence_number__max"]


def check_if_current_approver(approval):
    sequence_min_value = retrieve_sequence_min(approval.requisition)

    return approval.sequence_number == sequence_min_value


def check_fully_approved(requisition):
    if (
        retrieve_sequence_min(requisition) is None
        and requisition.status == RequisitionStatusChoices.PENDING_APPROVAL
        and requisition.approved_at is None
    ):
        requisition.status = RequisitionStatusChoices.APPROVED
        requisition.approved_at = timezone.now()

        requisition.save()

        send_fully_approved_email.delay(requisition.id)  # type: ignore


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
            approval.notified_at = approval.updated_at = timestamp

            approval.save()

            send_approval_email.delay(requisition.id, approval.id)  # type: ignore
