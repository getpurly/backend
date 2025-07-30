from django.contrib import admin

from .forms import ApprovalChainForm, ApprovalChainHeaderRuleForm, ApprovalChainLineRuleForm
from .models import (
    Approval,
    ApprovalChain,
    ApprovalChainHeaderRule,
    ApprovalChainLineRule,
    ApprovalGroup,
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
    list_display = [
        "id",
        "requisition__id",
        "approver__username",
        "sequence_number",
        "status",
        "notified_at",
        "approved_at",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
    ]
    list_filter = ["status", "notified_at", "approved_at", "created_at", "updated_at"]
    search_fields = []
    readonly_fields = ["created_at", "created_by", "updated_at", "updated_by"]

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if change:
            obj.updated_by = request.user
        else:
            obj.created_by = request.user
            obj.updated_by = request.user

        return super().save_model(request, obj, form, change)


class ApprovalChainAdmin(admin.ModelAdmin):
    form = ApprovalChainForm
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
    list_filter = ["approver_mode", "created_at", "updated_at", "active"]
    search_fields = []
    readonly_fields = ["created_at", "created_by", "updated_at", "updated_by"]
    inlines = [ApprovalChainHeaderRuleInline, ApprovalChainLineRuleInline]

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
    list_display = [
        "id",
        "name",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
    ]
    list_filter = ["created_at", "updated_at"]
    search_fields = []
    readonly_fields = ["created_at", "created_by", "updated_at", "updated_by"]

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
    form = ApprovalChainHeaderRuleForm
    list_display = [
        "id",
        "approval_chain__name",
        "field",
        "operator",
        "value",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
    ]
    list_filter = ["field", "operator", "created_at", "updated_at"]
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
    form = ApprovalChainLineRuleForm
    list_display = [
        "id",
        "approval_chain__name",
        "field",
        "operator",
        "match_mode",
        "value",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
    ]
    list_filter = ["field", "operator", "created_at", "updated_at"]
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
