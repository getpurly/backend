from django.utils import timezone
from rest_framework import exceptions

from config.exceptions import BadRequest
from purly.approval.services import cancel_approvals, generate_approvals

from .models import RequisitionStatusChoices


def submit_withdraw_validation(request_user, action, requisition):
    if requisition.owner != request_user:
        raise exceptions.PermissionDenied(f"You must be the requisition owner to {action}.")

    if action == "submit":
        if requisition.status == RequisitionStatusChoices.PENDING_APPROVAL:
            raise BadRequest(detail="This requisition has already been submitted.")

        if requisition.status != RequisitionStatusChoices.DRAFT:
            raise BadRequest(
                detail="This requisition must be in draft status to submit for approval."
            )

        if generate_approvals(requisition) is False:
            msg = "This requisition cannot be submitted because no approval chains matched."

            raise BadRequest(detail=msg)
    else:
        if requisition.status == RequisitionStatusChoices.DRAFT:
            raise BadRequest(detail="This requisition has already been withdrawn.")

        if requisition.status != RequisitionStatusChoices.PENDING_APPROVAL:
            raise BadRequest(
                detail="This requisition must be in pending approval status to withdraw."
            )


def on_submit(requisition):
    requisition.status = RequisitionStatusChoices.PENDING_APPROVAL
    requisition.submitted_at = timezone.now()
    requisition.rejected_at = None

    requisition.save()

    return requisition


def on_withdraw_cleanup(requisition):
    cancel_approvals(requisition)

    requisition.status = RequisitionStatusChoices.DRAFT
    requisition.submitted_at = None

    requisition.save()

    return requisition
