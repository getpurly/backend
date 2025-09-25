from django.contrib import messages
from django.db import transaction

from purly.approval.models import ApprovalStatusChoices
from purly.approval.services import check_fully_approved, notify_current_sequence
from purly.requisition.models import Requisition, RequisitionStatusChoices
from purly.requisition.services import on_withdraw


@transaction.atomic
def admin_action_delete(self, request, queryset, model_name):
    changed = 0
    requisitions = set()

    for instance in queryset:
        if instance.deleted:
            continue

        instance.deleted = True
        instance.updated_by = request.user

        if model_name == "approvals":
            requisitions.add(instance.requisition_id)

            if instance.status == ApprovalStatusChoices.PENDING:
                instance.status = ApprovalStatusChoices.CANCELLED

        if model_name == "approval chains":
            instance.active = False

        if model_name == "requisitions":
            lines = instance.lines.all()

            for line in lines:
                line.deleted = True
                line.updated_by = request.user

                line.save()

            if instance.status == RequisitionStatusChoices.PENDING_APPROVAL:
                on_withdraw(instance)

        instance.save()

        changed += 1

    if model_name == "approvals" and requisitions:
        for requisition_id in requisitions:
            requisition = Requisition.objects.get(pk=requisition_id)

            transaction.on_commit(
                lambda requisition=requisition: notify_current_sequence(requisition)
            )
            transaction.on_commit(lambda requisition=requisition: check_fully_approved(requisition))

    match changed:
        case 0:
            self.message_user(request, f"No {model_name} were eligible.", level=messages.WARNING)
        case _:
            self.message_user(
                request,
                f"The selected {model_name} were soft deleted (total = {changed}).",
                level=messages.SUCCESS,
            )
