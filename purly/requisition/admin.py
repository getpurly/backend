from django.contrib import admin, messages
from django.db import transaction
from django.http import HttpResponseRedirect

from purly.approval.models import Approval
from purly.approval.services import generate_approvals
from purly.requisition.services import on_submit, on_withdraw

from .forms import RequisitionForm, RequisitionLineForm
from .models import Requisition, RequisitionLine, RequisitionStatusChoices


def admin_action_results(self, request, action, changed):
    match changed:
        case 0:
            self.message_user(request, "No requisitions were eligible.", level=messages.WARNING)
        case _:
            self.message_user(
                request,
                f"The selected requisitions were {action} (total = {changed}).",
                level=messages.SUCCESS,
            )


class RequisitionLineInline(admin.StackedInline):
    autocomplete_fields = ["ship_to"]
    model = RequisitionLine
    extra = 1
    verbose_name = "requisition line"
    verbose_name_plural = "requisition lines"
    readonly_fields = ["created_at", "created_by", "updated_at", "updated_by", "deleted"]


class RequisitionAdmin(admin.ModelAdmin):
    actions = ["submit", "withdraw"]
    autocomplete_fields = ["owner", "project"]
    change_form_template = "admin/requisition/change_form.html"
    form = RequisitionForm
    fields = [
        "name",
        "external_reference",
        "status",
        "owner",
        "project",
        "supplier",
        "justification",
        "total_amount",
        "currency",
        "submitted_at",
        "approved_at",
        "rejected_at",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
        "deleted",
    ]
    list_display = [
        "id",
        "name",
        "external_reference",
        "status",
        "owner",
        "project",
        "supplier",
        "justification",
        "total_amount",
        "currency",
        "submitted_at",
        "approved_at",
        "rejected_at",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
    ]
    list_filter = [
        "status",
        "submitted_at",
        "approved_at",
        "rejected_at",
        "created_at",
        "updated_at",
        "submitted_at",
        "approved_at",
        "rejected_at",
        "deleted",
    ]
    search_fields = [
        "id",
        "name",
        "external_reference",
        "status",
        "owner__username",
        "project__name",
        "supplier",
        "justification",
        "total_amount",
        "currency",
        "created_by__username",
        "updated_by__username",
    ]
    inlines = [RequisitionLineInline]

    @transaction.atomic
    @admin.action(description="Submit for approval")
    def submit(self, request, queryset):
        changed = 0

        for requisition in queryset:
            if requisition.status != RequisitionStatusChoices.DRAFT:
                continue

            if generate_approvals(requisition) is False:
                continue

            on_submit(requisition, request_user=request.user)

            changed += 1

        admin_action_results(self, request, "submitted", changed)

    @transaction.atomic
    @admin.action(description="Withdraw from approval")
    def withdraw(self, request, queryset):
        changed = 0

        for requisition in queryset:
            if requisition.status != RequisitionStatusChoices.PENDING_APPROVAL:
                continue

            on_withdraw(requisition, request_user=request.user)

            changed += 1

        admin_action_results(self, request, "withdrawn", changed)

    @transaction.atomic
    def response_change(self, request, obj):
        if "_submit" in request.POST or "_withdraw" in request.POST:
            if "_submit" in request.POST:
                if obj.status != RequisitionStatusChoices.DRAFT:
                    self.message_user(
                        request,
                        "This requisition must be in draft status to submit for approval.",
                        level=messages.WARNING,
                    )

                    return HttpResponseRedirect(request.path)

                if generate_approvals(obj) is False:
                    self.message_user(
                        request,
                        "This requisition cannot be submitted because no approval chains matched.",
                        level=messages.WARNING,
                    )

                    return HttpResponseRedirect(request.path)

                on_submit(obj)

                self.message_user(
                    request,
                    "This requisition has been submitted for approval.",
                    level=messages.SUCCESS,
                )

                return HttpResponseRedirect(request.path)

            if "_withdraw" in request.POST:
                if obj.status != RequisitionStatusChoices.PENDING_APPROVAL:
                    self.message_user(
                        request,
                        "This requisition must be in pending approval status to withdraw.",
                        level=messages.WARNING,
                    )

                    return HttpResponseRedirect(request.path)

                on_withdraw(obj)

                self.message_user(
                    request, "This requisition has been withdrawn.", level=messages.SUCCESS
                )

                return HttpResponseRedirect(request.path)

        return super().response_change(request, obj)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        if (
            request.path.endswith("/autocomplete/")
            and request.GET.get("app_label") == Approval._meta.app_label
        ):
            queryset = (
                queryset.active()  # type: ignore
                .filter(status=RequisitionStatusChoices.PENDING_APPROVAL)
                .order_by("id")
            )

        if (
            request.path.endswith("/autocomplete/")
            and request.GET.get("app_label") == RequisitionLine._meta.app_label
        ):
            queryset = (
                queryset.active().filter(status=RequisitionStatusChoices.DRAFT).order_by("id")  # type: ignore
            )

        return queryset, use_distinct

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [
            "status",
            "submitted_at",
            "approved_at",
            "rejected_at",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]

        if obj is None:
            return [*readonly_fields, "deleted"]

        return readonly_fields

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if change:
            obj.updated_by = request.user
        else:
            obj.created_by = request.user
            obj.updated_by = request.user

        return super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            if not instance.pk:
                instance.created_by = request.user
                instance.updated_by = request.user
            else:
                instance.updated_by = request.user

            instance.save()

        for instance in formset.deleted_objects:
            instance.delete()

        formset.save_m2m()


class RequisitionLineAdmin(admin.ModelAdmin):
    autocomplete_fields = ["requisition", "ship_to"]
    form = RequisitionLineForm
    fields = [
        "line_number",
        "line_type",
        "description",
        "category",
        "manufacturer",
        "manufacturer_part_number",
        "quantity",
        "unit_of_measure",
        "unit_price",
        "line_total",
        "payment_term",
        "need_by",
        "requisition",
        "ship_to",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
        "deleted",
    ]
    list_display = [
        "id",
        "line_number",
        "line_type",
        "description",
        "category",
        "manufacturer",
        "manufacturer_part_number",
        "quantity",
        "unit_of_measure",
        "unit_price",
        "line_total",
        "payment_term",
        "need_by",
        "requisition__id",
        "ship_to",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
    ]
    list_filter = [
        "need_by",
        "created_at",
        "updated_at",
        "deleted",
    ]
    search_fields = [
        "description",
        "manufacturer",
        "manufacturer_part_number",
        "quantity",
        "unit_price",
        "line_total",
        "requisition__id",
        "ship_to__name",
        "created_by__username",
        "updated_by__username",
    ]

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ["created_at", "created_by", "updated_at", "updated_by"]

        if obj is None:
            return [*readonly_fields, "deleted"]

        return readonly_fields

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if change:
            obj.updated_by = request.user
        else:
            obj.created_by = request.user
            obj.updated_by = request.user

        return super().save_model(request, obj, form, change)


admin.site.register(Requisition, RequisitionAdmin)
admin.site.register(RequisitionLine, RequisitionLineAdmin)
