from django.contrib import admin

from .models import Requisition, RequisitionLine


class RequisitionLineInline(admin.StackedInline):
    model = RequisitionLine
    extra = 1
    verbose_name = "requisition line"
    verbose_name_plural = "requisition lines"
    readonly_fields = ["created_at", "created_by", "updated_at", "updated_by"]


class RequisitionAdmin(admin.ModelAdmin):
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
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
        "submitted_at",
        "approved_at",
    ]
    list_filter = [
        "created_at",
        "updated_at",
        "submitted_at",
        "approved_at",
    ]
    search_fields = [
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
    readonly_fields = ["created_at", "created_by", "updated_at", "updated_by"]
    inlines = [RequisitionLineInline]

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
    list_display = [
        "id",
        "line_number",
        "line_type",
        "description",
        "category",
        "manufacturer",
        "manufacturer_part_number",
        "quantity",
        "uom",
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


admin.site.register(Requisition, RequisitionAdmin)
admin.site.register(RequisitionLine, RequisitionLineAdmin)
