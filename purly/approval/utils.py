from django.db import transaction
from django.db.models import Q

from .models import Approval, ApprovalChain, StatusChoices


def rule_matching(requisition, rule):
    if rule.external_reference and requisition.external_reference.lower() not in [
        val.lower() for val in rule.external_reference
    ]:
        return False

    if rule.owner and requisition.owner.username.lower() not in [val.lower() for val in rule.owner]:
        return False

    if rule.project and requisition.project.name.lower() not in [
        val.lower() for val in rule.project
    ]:
        return False

    if rule.supplier and requisition.supplier.lower() not in [val.lower() for val in rule.supplier]:
        return False

    if rule.currency and requisition.currency.lower() not in [val.lower() for val in rule.currency]:
        return False

    return True


@transaction.atomic
def generate_approvals(requisition):
    approvals = []

    rules = (
        ApprovalChain.objects.filter(min_amount__lte=requisition.total_amount)
        .filter(Q(max_amount__gte=requisition.total_amount) | Q(max_amount__isnull=True))
        .filter(active=True)
        .order_by("sequence_number")
    )

    for rule in rules:
        if rule_matching(requisition, rule):
            approval = Approval(
                requisition=requisition,
                approver=rule.approver,
                sequence_number=rule.sequence_number,
                status=StatusChoices.PENDING,
            )

            approvals.append(approval)

    Approval.objects.bulk_create(approvals)
