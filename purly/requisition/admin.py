from decimal import Decimal

from django.contrib import admin, messages
from django.db import transaction
from django.db.models import Q, Sum
from django.http import HttpResponseRedirect

from purly.approval.models import Approval
from purly.approval.services import bypass_approvals, generate_approvals
from purly.base import AdminBase
from purly.requisition.services import on_submit, on_withdraw
from purly.utils import admin_action_delete

from .forms import RequisitionForm, RequisitionLineForm, RequisitionLineInlineFormSet
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
    form = RequisitionLineForm
    formset = RequisitionLineInlineFormSet
    model = RequisitionLine
    min_num = 1
    validate_min = True
    extra = 0
    verbose_name = "requisition line"
    verbose_name_plural = "requisition lines"
    readonly_fields = ["created_at", "created_by", "updated_at", "updated_by", "deleted"]

    def has_add_permission(self, request, obj=None):
        return not (
            obj
            and obj.status
            not in [RequisitionStatusChoices.DRAFT, RequisitionStatusChoices.REJECTED]
        )

    def has_delete_permission(self, request, obj=None):
        return not (
            obj
            and obj.status
            not in [RequisitionStatusChoices.DRAFT, RequisitionStatusChoices.REJECTED]
        )


class RequisitionAdmin(AdminBase):
    actions = ["submit", "withdraw", "delete"]
    autocomplete_fields = ["owner", "project"]
    change_form_template = "admin/requisition/change_form.html"
    form = RequisitionForm
    inlines = [RequisitionLineInline]
    fieldsets = (
        (
            "Basic Settings",
            {
                "fields": ("name",),
            },
        ),
        (
            "Requisition Information",
            {
                "fields": (
                    "external_reference",
                    "status",
                    "owner",
                    "project",
                    "supplier",
                    "justification",
                    "total_amount",
                    "currency",
                ),
            },
        ),
        (
            "Misc",
            {
                "fields": (
                    "submitted_at",
                    "approved_at",
                    "rejected_at",
                    "created_at",
                    "created_by",
                    "updated_at",
                    "updated_by",
                    "deleted",
                ),
            },
        ),
    )
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
        "deleted",
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

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        return queryset.select_related(
            "project", "owner", "created_by", "updated_by"
        ).prefetch_related("lines")

    @transaction.atomic
    @admin.action(description="Submit for approval for selected requisitions")
    def submit(self, request, queryset):
        changed = 0

        for requisition in queryset:
            if requisition.status not in [
                RequisitionStatusChoices.DRAFT,
                RequisitionStatusChoices.REJECTED,
            ]:
                continue

            success, _ = generate_approvals(requisition)

            if success is False:
                continue

            on_submit(requisition, request_user=request.user)

            changed += 1

        admin_action_results(self, request, "submitted", changed)

    @transaction.atomic
    @admin.action(description="Withdraw from approval for selected requisitions")
    def withdraw(self, request, queryset):
        changed = 0

        for requisition in queryset:
            if requisition.status != RequisitionStatusChoices.PENDING_APPROVAL:
                continue

            on_withdraw(requisition, request_user=request.user)

            changed += 1

        admin_action_results(self, request, "withdrawn", changed)

    @admin.action(description="Soft delete selected requisitions")
    def delete(self, request, queryset):
        admin_action_delete(self, request, queryset, "requisitions")

    @transaction.atomic
    def response_change(self, request, obj):  # noqa: PLR0911
        if "_submit" in request.POST or "_withdraw" in request.POST or "_bypass" in request.POST:
            if "_submit" in request.POST:
                if obj.status not in [
                    RequisitionStatusChoices.DRAFT,
                    RequisitionStatusChoices.REJECTED,
                ]:
                    self.message_user(
                        request,
                        "This requisition must be in draft or rejected status to submit.",
                        level=messages.WARNING,
                    )

                    return HttpResponseRedirect(request.path)

                success, error = generate_approvals(obj)

                if success is False:
                    self.message_user(
                        request,
                        error,
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

            if "_bypass" in request.POST:
                if obj.status != RequisitionStatusChoices.PENDING_APPROVAL:
                    self.message_user(
                        request,
                        "This requisition must be in pending approval status to bypass approvals.",
                        level=messages.WARNING,
                    )

                    return HttpResponseRedirect(request.path)

                bypass_approvals(obj, request.user)

                self.message_user(
                    request, "Bypassed approvals for this requisition.", level=messages.SUCCESS
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
                queryset.active()  # type: ignore
                .filter(
                    Q(status=RequisitionStatusChoices.DRAFT)
                    | Q(status=RequisitionStatusChoices.REJECTED)
                )
                .order_by("id")
            )

        return queryset, use_distinct

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [
            "status",
            "total_amount",
            "submitted_at",
            "approved_at",
            "rejected_at",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
            "deleted",
        ]

        if obj and obj.deleted:
            return [field.name for field in self.model._meta.get_fields()]

        return readonly_fields

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

        total_amount = Decimal(
            form.instance.lines.aggregate(total_amount=Sum("line_total"))["total_amount"]
        )

        form.instance.total_amount = total_amount
        form.instance.save()


class RequisitionLineAdmin(AdminBase):
    fieldsets = (
        (
            "Requisition Line Information",
            {
                "fields": (
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
                ),
            },
        ),
        (
            "Misc",
            {
                "fields": (
                    "created_at",
                    "created_by",
                    "updated_at",
                    "updated_by",
                    "deleted",
                ),
            },
        ),
    )
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
        "deleted",
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

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        return queryset.select_related("requisition", "ship_to", "created_by", "updated_by")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(Requisition, RequisitionAdmin)
admin.site.register(RequisitionLine, RequisitionLineAdmin)
