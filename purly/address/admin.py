from django.contrib import admin

from purly.address.forms import AddressForm
from purly.utils import AdminBase, admin_action_delete

from .models import Address


class AddressAdmin(AdminBase):
    form = AddressForm
    actions = ["delete"]
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
        "owner__username",
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
        "created_by__username",
        "updated_by__username",
    ]

    @admin.action(description="Soft delete selected addresses")
    def delete(self, request, queryset):
        admin_action_delete(self, request, queryset, "addresses")


admin.site.register(Address, AddressAdmin)
