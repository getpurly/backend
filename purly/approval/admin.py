from django.contrib import admin

from .forms import ApprovalChainRuleForm
from .models import Approval, ApprovalChain, ApprovalChainRule


class ApprovalChainRuleInline(admin.StackedInline):
    form = ApprovalChainRuleForm
    model = ApprovalChainRule
    extra = 1
    verbose_name = "approval chain rule"
    verbose_name_plural = "approval chain rules"
    readonly_fields = ["created_at", "created_by", "updated_at", "updated_by"]


class ApprovalAdmin(admin.ModelAdmin):
    list_display = [
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
    list_display = [
        "name",
        "approver__username",
        "sequence_number",
        "min_amount",
        "max_amount",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
        "active",
    ]
    list_filter = ["created_at", "updated_at", "active"]
    search_fields = []
    readonly_fields = ["created_at", "created_by", "updated_at", "updated_by"]
    inlines = [ApprovalChainRuleInline]

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


class ApprovalChainRuleAdmin(admin.ModelAdmin):
    form = ApprovalChainRuleForm
    list_display = [
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


admin.site.register(Approval, ApprovalAdmin)
admin.site.register(ApprovalChain, ApprovalChainAdmin)
admin.site.register(ApprovalChainRule, ApprovalChainRuleAdmin)
