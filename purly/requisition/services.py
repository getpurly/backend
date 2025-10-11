from django.db import transaction
from django.utils import timezone
from rest_framework import exceptions

from config.exceptions import BadRequest
from purly.approval.emails import send_reject_email

from .models import RequisitionStatusChoices


def submit_withdraw_validation(request_user, requisition, action):
    from purly.approval.services import generate_approvals

    if requisition.owner != request_user:
        raise exceptions.PermissionDenied(f"You must be the requisition owner to {action}.")

    if action == "submit":
        if requisition.status == RequisitionStatusChoices.PENDING_APPROVAL:
            raise BadRequest(detail="This requisition has already been submitted.")

        if requisition.status not in [
            RequisitionStatusChoices.DRAFT,
            RequisitionStatusChoices.REJECTED,
        ]:
            raise BadRequest(
                detail="This requisition must be in draft or rejected status to submit."
            )

        success, error = generate_approvals(requisition)

        if success is False:
            raise BadRequest(detail=error)

    else:
        if requisition.status == RequisitionStatusChoices.DRAFT:
            raise BadRequest(detail="This requisition has already been withdrawn.")

        if requisition.status != RequisitionStatusChoices.PENDING_APPROVAL:
            raise BadRequest(
                detail="This requisition must be in pending approval status to withdraw."
            )


def on_submit(requisition, **kwargs):
    from purly.approval.services import notify_current_sequence

    requisition.status = RequisitionStatusChoices.PENDING_APPROVAL
    requisition.submitted_at = timezone.now()
    requisition.rejected_at = None

    request_user = kwargs.get("request_user")

    if request_user:
        requisition.updated_by = request_user

    requisition.save()

    transaction.on_commit(lambda: notify_current_sequence(requisition))

    return requisition


def on_withdraw(requisition, **kwargs):
    from purly.approval.services import cancel_approvals

    cancel_approvals(requisition)

    requisition.status = RequisitionStatusChoices.DRAFT
    requisition.submitted_at = None

    request_user = kwargs.get("request_user")

    if request_user:
        requisition.updated_by = request_user

    requisition.save()

    return requisition


def on_reject_requisition(approval, requisition):
    requisition.status = RequisitionStatusChoices.REJECTED
    requisition.submitted_at = None
    requisition.rejected_at = timezone.now()

    requisition.save()

    transaction.on_commit(lambda: send_reject_email.delay(requisition.id, approval.id))  # type: ignore

    return requisition
