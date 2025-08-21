from django.contrib import admin, messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.utils import timezone

from purly.requisition.models import Requisition
from purly.user.models import User

from .forms import ApprovalChainForm, ApprovalChainHeaderRuleForm, ApprovalChainLineRuleForm
from .models import (
    Approval,
    ApprovalChain,
    ApprovalChainHeaderRule,
    ApprovalChainLineRule,
    ApprovalGroup,
    ApprovalStatusChoices,
)
from .services import (
    check_if_current_approver,
    notify_current_sequence,
    on_fully_approved,
    on_reject,
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


class ApprovalAdmin(admin.ModelAdmin):
    actions = ["approve", "reject", "skip"]
    autocomplete_fields = ["approver", "requisition"]
    change_form_template = "admin/approval/change_form.html"
    fields = [
        "requisition",
        "approver",
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
    ]
    search_fields = []

    @transaction.atomic
    @admin.action(description="Set approved (only if current approver)")
    def approve(self, request, queryset):
        changed = 0
        requisitions = set()
        timestamp = timezone.now()

        for approval in queryset:
            if (
                check_if_current_approver(approval) is False
                and approval.status == ApprovalStatusChoices.PENDING
            ):
                continue

            if approval.status != ApprovalStatusChoices.PENDING:
                continue

            approval.status = ApprovalStatusChoices.APPROVED
            approval.approved_at = timestamp
            approval.updated_by = request.user

            approval.save()

            changed += 1

            requisition_id = approval.requisition.id

            if requisition_id not in requisitions:
                transaction.on_commit(
                    lambda requisition_id=requisition_id: notify_current_sequence(
                        Requisition.objects.get(pk=requisition_id)
                    )
                )
                transaction.on_commit(
                    lambda requisition_id=requisition_id: on_fully_approved(
                        Requisition.objects.get(pk=requisition_id)
                    )
                )

                requisitions.add(requisition_id)

        admin_action_results(self, request, "approved", changed)

    @transaction.atomic
    @admin.action(description="Set rejected (only if current approver)")
    def reject(self, request, queryset):
        changed = 0
        requisitions = set()
        timestamp = timezone.now()

        for approval in queryset:
            if (
                check_if_current_approver(approval) is False
                and approval.status == ApprovalStatusChoices.PENDING
            ):
                continue

            if approval.status != ApprovalStatusChoices.PENDING:
                continue

            approval.status = ApprovalStatusChoices.REJECTED
            approval.rejected_at = timestamp
            approval.updated_by = request.user

            approval.save()

            changed += 1

            requisition_id = approval.requisition.id

            if requisition_id not in requisitions:
                transaction.on_commit(
                    lambda approval=approval, requisition_id=requisition_id: on_reject(
                        approval, Requisition.objects.get(pk=requisition_id)
                    )
                )

                requisitions.add(requisition_id)

        admin_action_results(self, request, "rejected", changed)

    @transaction.atomic
    @admin.action(description="Set skipped (only if current approver)")
    def skip(self, request, queryset):
        changed = 0
        requisitions = set()
        timestamp = timezone.now()

        for approval in queryset:
            if (
                check_if_current_approver(approval) is False
                and approval.status == ApprovalStatusChoices.PENDING
            ):
                continue

            if approval.status != ApprovalStatusChoices.PENDING:
                continue

            approval.status = ApprovalStatusChoices.SKIPPED
            approval.skipped_at = timestamp
            approval.updated_by = request.user

            approval.save()

            changed += 1

            requisition_id = approval.requisition.id

            if requisition_id not in requisitions:
                transaction.on_commit(
                    lambda requisition_id=requisition_id: notify_current_sequence(
                        Requisition.objects.get(pk=requisition_id)
                    )
                )
                transaction.on_commit(
                    lambda requisition_id=requisition_id: on_fully_approved(
                        Requisition.objects.get(pk=requisition_id)
                    )
                )

                requisitions.add(requisition_id)

        admin_action_results(self, request, "skipped", changed)

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return [
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

        return [
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
        ]

    @transaction.atomic
    def response_change(self, request, obj):
        if "_approve" in request.POST or "_reject" in request.POST or "_skip" in request.POST:
            timestamp = timezone.now()

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
                obj.status = ApprovalStatusChoices.APPROVED
                obj.approved_at = timestamp
                obj.updated_by = request.user

                obj.save()

                transaction.on_commit(lambda: notify_current_sequence(obj.requisition))
                transaction.on_commit(lambda: on_fully_approved(obj.requisition))

                self.message_user(
                    request, "This approval has been approved.", level=messages.SUCCESS
                )

                return HttpResponseRedirect(request.path)

            if "_reject" in request.POST:
                obj.status = ApprovalStatusChoices.REJECTED
                obj.rejected_at = timestamp
                obj.updated_by = request.user

                obj.save()

                transaction.on_commit(lambda: on_reject(obj, obj.requisition))

                self.message_user(
                    request, "This approval has been rejected.", level=messages.SUCCESS
                )

                return HttpResponseRedirect(request.path)

            if "_skip" in request.POST:
                obj.status = ApprovalStatusChoices.SKIPPED
                obj.skipped_at = timestamp
                obj.updated_by = request.user

                obj.save()

                transaction.on_commit(lambda: notify_current_sequence(obj.requisition))
                transaction.on_commit(lambda: on_fully_approved(obj.requisition))

                self.message_user(
                    request, "This approval has been skipped.", level=messages.SUCCESS
                )

                return HttpResponseRedirect(request.path)

        return super().response_change(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if change:
            obj.updated_by = request.user
        else:
            obj.system_generated = False
            obj.created_by = request.user
            obj.updated_by = request.user

        return super().save_model(request, obj, form, change)


class ApprovalChainAdmin(admin.ModelAdmin):
    autocomplete_fields = ["approver", "approver_group"]
    form = ApprovalChainForm
    fields = [
        "name",
        "approver_mode",
        "approver",
        "approver_group",
        "sequence_number",
        "min_amount",
        "max_amount",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
        "active",
        "deleted",
    ]
    list_display = [
        "id",
        "name",
        "approver_mode",
        "approver__username",
        "approver_group__name",
        "sequence_number",
        "min_amount",
        "max_amount",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
        "active",
    ]
    list_filter = ["approver_mode", "created_at", "updated_at", "active", "deleted"]
    search_fields = ["name"]
    inlines = [ApprovalChainHeaderRuleInline, ApprovalChainLineRuleInline]

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        if request.path.endswith("/autocomplete/"):
            queryset = ApprovalChain.objects.active().all()  # type: ignore

        return queryset, use_distinct

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ["created_at", "created_by", "updated_at", "updated_by"]

        if obj is None:
            return [*readonly_fields, "active", "deleted"]

        return readonly_fields

    def has_delete_permission(self, request, obj=None):
        return False

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

    def save_model(self, request, obj, form, change):
        if change:
            obj.updated_by = request.user
        else:
            obj.created_by = request.user
            obj.updated_by = request.user

        return super().save_model(request, obj, form, change)


class ApprovalGroupAdmin(admin.ModelAdmin):
    fields = [
        "name",
        "description",
        "approver",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
        "deleted",
    ]
    list_display = [
        "id",
        "name",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
    ]
    list_filter = ["created_at", "updated_at", "deleted"]
    filter_horizontal = ["approver"]
    search_fields = ["name"]

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        if request.path.endswith("/autocomplete/"):
            queryset = ApprovalGroup.objects.active().all()  # type: ignore

        return queryset, use_distinct

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "approver":
            kwargs["queryset"] = User.objects.filter(is_active=True)

        return super().formfield_for_manytomany(db_field, request, **kwargs)

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


class ApprovalChainHeaderRuleAdmin(admin.ModelAdmin):
    autocomplete_fields = ["approval_chain"]
    form = ApprovalChainHeaderRuleForm
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
