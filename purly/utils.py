from django.contrib import messages
from django.db import transaction


@transaction.atomic
def admin_action_delete(self, request, queryset, model_name):
    changed = 0

    for instance in queryset:
        if instance.deleted:
            continue

        instance.deleted = True
        instance.updated_by = request.user

        if model_name == "approval chains":
            instance.active = False

        if model_name == "requisitions":
            lines = instance.lines.all()

            for line in lines:
                line.deleted = True
                line.updated_by = request.user

                line.save()

        instance.save()

        changed += 1

    match changed:
        case 0:
            self.message_user(request, f"No {model_name} were eligible.", level=messages.WARNING)
        case _:
            self.message_user(
                request,
                f"The selected {model_name} were soft deleted (total = {changed}).",
                level=messages.SUCCESS,
            )
