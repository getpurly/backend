from django.contrib import admin

from purly.address.forms import AddressForm
from purly.base import AdminBase
from purly.utils import admin_action_delete

from .models import Address


class AddressAdmin(AdminBase):
    form = AddressForm
    actions = ["delete"]
    autocomplete_fields = ["owner"]
    fieldsets = (
        (
            "Basic Settings",
            {
                "fields": (
                    "owner",
                    "name",
                ),
            },
        ),
        (
            "Address Information",
            {
                "fields": (
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
                ),
            },
        ),
        (
            "Misc",
            {
                "classes": ["collapse"],
                "fields": ("created_at", "created_by", "updated_at", "updated_by", "deleted"),
            },
        ),
    )
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
        "delivery_instructions",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
        "deleted",
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

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        return queryset.select_related("owner", "created_by", "updated_by")

    @admin.action(description="Soft delete selected addresses")
    def delete(self, request, queryset):
        admin_action_delete(self, request, queryset, "addresses")


admin.site.register(Address, AddressAdmin)
