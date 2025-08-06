from django.contrib import admin

from .models import Address


class AddressAdmin(admin.ModelAdmin):
    autocomplete_fields = ["owner"]
    list_display = [
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
        "owner",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
    ]
    list_filter = ["created_at", "updated_at"]
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


admin.site.register(Address, AddressAdmin)
