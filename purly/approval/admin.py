from django.contrib import admin, messages
from django.db import transaction
from django.http import HttpResponseRedirect

from purly.base import AdminBase
from purly.requisition.models import Requisition
from purly.user.models import User
from purly.utils import admin_action_delete

from .forms import (
    ApprovalChainForm,
    ApprovalChainHeaderRuleForm,
    ApprovalChainLineRuleForm,
    ApprovalForm,
    ApprovalGroupForm,
)
from .models import (
    Approval,
    ApprovalChain,
    ApprovalChainHeaderRule,
    ApprovalChainLineRule,
    ApprovalGroup,
    ApprovalStatusChoices,
)
from .services import (
    check_fully_approved,
    check_if_current_approver,
    notify_current_sequence,
    on_approve_skip,
    on_reject,
    on_reject_requisition,
    retrieve_sequence_max,
)


def admin_action_results(self, request, action, changed):
    match changed:
        case 0:
            self.message_user(
                request, "No pending approvals were eligible.", level=messages.WARNING
            )
        case _:
            self.message_user(
                request,
                f"The selected approvals were {action} (total = {changed}).",
                level=messages.SUCCESS,
            )


def is_actionable(approval):
    if (  # noqa: SIM103
        check_if_current_approver(approval) is False
        or approval.status != ApprovalStatusChoices.PENDING
    ):
        return False

    return True


class ApprovalChainHeaderRuleInline(admin.StackedInline):
    form = ApprovalChainHeaderRuleForm
    model = ApprovalChainHeaderRule
    extra = 0
    verbose_name = "header rule"
    verbose_name_plural = "header rules"
    readonly_fields = ["created_at", "created_by", "updated_at", "updated_by"]


class ApprovalChainLineRuleInline(admin.StackedInline):
    form = ApprovalChainLineRuleForm
    model = ApprovalChainLineRule
    extra = 0
    verbose_name = "line rule"
    verbose_name_plural = "line rules"
    readonly_fields = ["created_at", "created_by", "updated_at", "updated_by"]


class ApprovalAdmin(AdminBase):
    actions = ["approve", "reject", "skip", "delete"]
    autocomplete_fields = ["approver", "requisition"]
    change_form_template = "admin/approval/change_form.html"
    form = ApprovalForm
    fieldsets = (
        (
            "Basic Settings",
            {
                "fields": ("requisition", "approver"),
            },
        ),
        (
            "Approval Information",
            {
                "fields": (
                    "sequence_number",
                    "status",
                    "comment",
                    "rule_metadata",
                    "system_generated",
                ),
            },
        ),
        (
            "Misc",
            {
                "fields": (
                    "notified_at",
                    "approved_at",
                    "rejected_at",
                    "skipped_at",
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
        "requisition__id",
        "approver__username",
        "sequence_number",
        "status",
        "system_generated",
        "notified_at",
        "approved_at",
        "rejected_at",
        "skipped_at",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
        "deleted",
    ]
    list_filter = [
        "status",
        "system_generated",
        "notified_at",
        "approved_at",
        "rejected_at",
        "skipped_at",
        "created_at",
        "updated_at",
        "deleted",
    ]
    search_fields = []

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        return queryset.select_related("approver", "requisition", "created_by", "updated_by")

    @transaction.atomic
    @admin.action(description="Set approved (only if current approver) for selected approvals")
    def approve(self, request, queryset):
        changed = 0
        requisitions = set()

        for approval in queryset:
            if not is_actionable(approval):
                continue

            on_approve_skip(
                approval,
                approval.requisition,
                "approve",
                request_user=request.user,
                send_email=False,
            )

            changed += 1

            requisitions.add(approval.requisition_id)

        for requisition_id in requisitions:
            transaction.on_commit(
                lambda requisition_id=requisition_id: notify_current_sequence(
                    Requisition.objects.get(pk=requisition_id)
                )
            )
            transaction.on_commit(
                lambda requisition_id=requisition_id: check_fully_approved(
                    Requisition.objects.get(pk=requisition_id)
                )
            )

        admin_action_results(self, request, "approved", changed)

    @transaction.atomic
    @admin.action(description="Set rejected (only if current approver) for selected approvals")
    def reject(self, request, queryset):
        changed = 0
        requisitions = set()

        for approval in queryset:
            if not is_actionable(approval):
                continue

            on_reject(approval, approval.requisition, update_requisition=False)

            changed += 1

            requisition_id = approval.requisition.id

            if requisition_id not in requisitions:
                transaction.on_commit(
                    lambda approval=approval, requisition_id=requisition_id: on_reject_requisition(
                        approval, Requisition.objects.get(pk=requisition_id)
                    )
                )

                requisitions.add(requisition_id)

        admin_action_results(self, request, "rejected", changed)

    @transaction.atomic
    @admin.action(description="Set skipped (only if current approver) for selected approvals")
    def skip(self, request, queryset):
        changed = 0
        requisitions = set()

        for approval in queryset:
            if not is_actionable(approval):
                continue

            on_approve_skip(
                approval,
                approval.requisition,
                "skip",
                request_user=request.user,
                send_email=False,
            )

            changed += 1

            requisitions.add(approval.requisition_id)

        for requisition_id in requisitions:
            transaction.on_commit(
                lambda requisition_id=requisition_id: notify_current_sequence(
                    Requisition.objects.get(pk=requisition_id)
                )
            )
            transaction.on_commit(
                lambda requisition_id=requisition_id: check_fully_approved(
                    Requisition.objects.get(pk=requisition_id)
                )
            )

        admin_action_results(self, request, "skipped", changed)

    @admin.action(description="Soft delete selected approvals")
    def delete(self, request, queryset):
        admin_action_delete(self, request, queryset, "approvals")

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [
            "requisition",
            "approver",
            "sequence_number",
            "status",
            "rule_metadata",
            "system_generated",
            "notified_at",
            "approved_at",
            "rejected_at",
            "skipped_at",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
            "deleted",
        ]

        if obj is None:
            return [
                "sequence_number",
                "status",
                "comment",
                "rule_metadata",
                "system_generated",
                "notified_at",
                "approved_at",
                "rejected_at",
                "skipped_at",
                "created_at",
                "created_by",
                "updated_at",
                "updated_by",
                "deleted",
            ]

        if obj and obj.deleted:
            return [field.name for field in self.model._meta.get_fields()]

        return readonly_fields

    def save_model(self, request, obj, form, change):
        if not change and obj.requisition_id:
            sequence_max = retrieve_sequence_max(obj.requisition)

            obj.sequence_number = sequence_max + 1

        if change:
            obj.updated_by = request.user
        else:
            obj.created_by = request.user
            obj.updated_by = request.user

        super().save_model(request, obj, form, change)

    @transaction.atomic
    def response_change(self, request, obj):
        if "_approve" in request.POST or "_reject" in request.POST or "_skip" in request.POST:
            if (
                check_if_current_approver(obj) is False
                and obj.status == ApprovalStatusChoices.PENDING
            ):
                self.message_user(
                    request, "An earlier approval is still pending.", level=messages.WARNING
                )

                return HttpResponseRedirect(request.path)

            if obj.status != ApprovalStatusChoices.PENDING:
                self.message_user(
                    request,
                    "This approval must be in pending status to update.",
                    level=messages.WARNING,
                )

                return HttpResponseRedirect(request.path)

            if "_approve" in request.POST:
                on_approve_skip(obj, obj.requisition, "approve")

                self.message_user(
                    request, "This approval has been approved.", level=messages.SUCCESS
                )

                return HttpResponseRedirect(request.path)

            if "_reject" in request.POST:
                on_reject(obj, obj.requisition)

                self.message_user(
                    request, "This approval has been rejected.", level=messages.SUCCESS
                )

                return HttpResponseRedirect(request.path)

            if "_skip" in request.POST:
                on_approve_skip(obj, obj.requisition, "skip")

                self.message_user(
                    request, "This approval has been skipped.", level=messages.SUCCESS
                )

                return HttpResponseRedirect(request.path)

        return super().response_change(request, obj)


class ApprovalChainAdmin(AdminBase):
    actions = ["activate", "deactivate", "delete"]
    autocomplete_fields = ["approver", "approver_group"]
    form = ApprovalChainForm
    fieldsets = (
        (
            "Basic Settings",
            {
                "fields": ("name",),
            },
        ),
        (
            "Approval Settings",
            {
                "fields": (
                    "approver_mode",
                    "approver",
                    "approver_group",
                    "group_mode",
                    "sequence_number",
                ),
            },
        ),
        (
            "Trigger Settings",
            {
                "fields": ("min_amount", "max_amount"),
            },
        ),
        (
            "Logic Settings",
            {
                "fields": ("header_rule_logic", "line_rule_logic", "cross_rule_logic"),
            },
        ),
        (
            "Effective Date Settings",
            {
                "fields": ("valid_from", "valid_to"),
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
                    "active",
                    "deleted",
                ),
            },
        ),
    )
    list_display = [
        "id",
        "name",
        "approver_mode",
        "approver__username",
        "approver_group__name",
        "group_mode",
        "sequence_number",
        "min_amount",
        "max_amount",
        "header_rule_logic",
        "line_rule_logic",
        "cross_rule_logic",
        "valid_from",
        "valid_to",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
        "active",
        "deleted",
    ]
    list_filter = [
        "approver_mode",
        "group_mode",
        "header_rule_logic",
        "line_rule_logic",
        "cross_rule_logic",
        "valid_from",
        "valid_to",
        "created_at",
        "updated_at",
        "active",
        "deleted",
    ]
    search_fields = ["name"]
    inlines = [ApprovalChainHeaderRuleInline, ApprovalChainLineRuleInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        return queryset.select_related("approver", "created_by", "updated_by")

    @admin.action(description="Active selected approval chains")
    def activate(self, request, queryset):
        changed = 0

        for approval_chain in queryset:
            if approval_chain.deleted is False and approval_chain.active is False:
                approval_chain.active = True

                changed += 1

                approval_chain.save()

        match changed:
            case 0:
                self.message_user(
                    request, "No approval chains were eligible.", level=messages.WARNING
                )
            case _:
                self.message_user(
                    request,
                    f"The selected approval chains were activated (total = {changed}).",
                    level=messages.SUCCESS,
                )

    @admin.action(description="Deactive selected approval chains")
    def deactivate(self, request, queryset):
        changed = 0

        for approval_chain in queryset:
            if approval_chain.deleted is False and approval_chain.active is True:
                approval_chain.active = False

                changed += 1

                approval_chain.save()

        match changed:
            case 0:
                self.message_user(
                    request, "No approval chains were eligible.", level=messages.WARNING
                )
            case _:
                self.message_user(
                    request,
                    f"The selected approval chains were activated (total = {changed}).",
                    level=messages.SUCCESS,
                )

    @admin.action(description="Soft delete selected approval chains")
    def delete(self, request, queryset):
        admin_action_delete(self, request, queryset, "approval chains")

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        if request.path.endswith("/autocomplete/"):
            queryset = queryset.active().filter(active=True).order_by("name")  # type: ignore

        return queryset, use_distinct

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ["created_at", "created_by", "updated_at", "updated_by", "deleted"]

        if obj is None:
            return [*readonly_fields, "active"]

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


class ApprovalGroupAdmin(AdminBase):
    actions = ["delete"]
    form = ApprovalGroupForm
    fieldsets = (
        (
            "Basic Settings",
            {
                "fields": ("name",),
            },
        ),
        (
            "Group Information",
            {
                "fields": ("description",),
            },
        ),
        (
            "Approver Settings",
            {
                "fields": ("approver",),
            },
        ),
        (
            "Misc",
            {
                "fields": ("created_at", "created_by", "updated_at", "updated_by", "deleted"),
            },
        ),
    )
    list_display = [
        "id",
        "name",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
        "deleted",
    ]
    list_filter = ["created_at", "updated_at", "deleted"]
    filter_horizontal = ["approver"]
    search_fields = ["name"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        return queryset.select_related("created_by", "updated_by")

    @admin.action(description="Soft delete selected approval groups")
    def delete(self, request, queryset):
        admin_action_delete(self, request, queryset, "approval groups")

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        if request.path.endswith("/autocomplete/"):
            queryset = queryset.active().order_by("name")  # type: ignore

        return queryset, use_distinct

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "approver":
            kwargs["queryset"] = User.objects.filter(is_active=True).order_by("username")

        return super().formfield_for_manytomany(db_field, request, **kwargs)


class ApprovalChainHeaderRuleAdmin(admin.ModelAdmin):
    autocomplete_fields = ["approval_chain"]
    form = ApprovalChainHeaderRuleForm
    fieldsets = (
        (
            "Rule Settings",
            {
                "fields": ("approval_chain", "field", "lookup", "value"),
            },
        ),
        (
            "Misc",
            {
                "fields": ("created_at", "created_by", "updated_at", "updated_by"),
            },
        ),
    )
    list_display = [
        "id",
        "approval_chain__name",
        "field",
        "lookup",
        "value",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
    ]
    list_filter = ["field", "lookup", "created_at", "updated_at"]
    search_fields = []
    readonly_fields = ["created_at", "created_by", "updated_at", "updated_by"]

    def save_model(self, request, obj, form, change):
        if change:
            obj.updated_by = request.user
        else:
            obj.created_by = request.user
            obj.updated_by = request.user

        return super().save_model(request, obj, form, change)


class ApprovalChainLineRuleAdmin(admin.ModelAdmin):
    autocomplete_fields = ["approval_chain"]
    form = ApprovalChainLineRuleForm
    fieldsets = (
        (
            "Rule Settings",
            {
                "fields": ("approval_chain", "match_mode", "field", "lookup", "value"),
            },
        ),
        (
            "Misc",
            {
                "fields": ("created_at", "created_by", "updated_at", "updated_by"),
            },
        ),
    )
    list_display = [
        "id",
        "approval_chain__name",
        "match_mode",
        "field",
        "lookup",
        "value",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
    ]
    list_filter = ["field", "lookup", "created_at", "updated_at"]
    search_fields = []
    readonly_fields = ["created_at", "created_by", "updated_at", "updated_by"]

    def save_model(self, request, obj, form, change):
        if change:
            obj.updated_by = request.user
        else:
            obj.created_by = request.user
            obj.updated_by = request.user

        return super().save_model(request, obj, form, change)


admin.site.register(Approval, ApprovalAdmin)
admin.site.register(ApprovalChain, ApprovalChainAdmin)
admin.site.register(ApprovalGroup, ApprovalGroupAdmin)
admin.site.register(ApprovalChainHeaderRule, ApprovalChainHeaderRuleAdmin)
admin.site.register(ApprovalChainLineRule, ApprovalChainLineRuleAdmin)
