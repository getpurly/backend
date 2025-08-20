from django.contrib import admin

from .models import Address


class AddressAdmin(admin.ModelAdmin):
    autocomplete_fields = ["owner"]
    fields = [
        "owner",
        "name",
        "address_code",
        "description",
        "attention",
        "phone",
        "street1",
        "street2",
        "city",
        "state",
        "zip_code",
        "country",
        "delivery_instructions",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
        "deleted",
    ]
    list_display = [
        "id",
        "owner",
        "name",
        "address_code",
        "description",
        "attention",
        "phone",
        "street1",
        "street2",
        "city",
        "state",
        "zip_code",
        "country",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
    ]
    list_filter = ["created_at", "updated_at", "deleted"]
    search_fields = [
        "id",
        "name",
        "address_code",
        "description",
        "attention",
        "phone",
        "street1",
        "street2",
        "city",
        "state",
        "zip_code",
        "country",
        "delivery_instructions",
        "owner__username",
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


admin.site.register(Address, AddressAdmin)
