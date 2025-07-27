from django.contrib import admin

from .models import Approval, ApprovalRule


class ApprovalAdmin(admin.ModelAdmin):
    list_display = [
        "requisition__id",
        "approver__username",
        "sequence_number",
        "status",
        "approved_at",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
    ]
    list_filter = ["status", "approved_at", "created_at", "updated_at"]
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


class ApprovalRuleAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "approver__username",
        "sequence_number",
        "external_reference",
        "owner",
        "project",
        "supplier",
        "min_total_amount",
        "max_total_amount",
        "currency",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
        "active",
    ]
    list_filter = ["created_at", "updated_at", "active"]
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


admin.site.register(Approval, ApprovalAdmin)
admin.site.register(ApprovalRule, ApprovalRuleAdmin)
