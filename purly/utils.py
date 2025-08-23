from django.contrib import admin, messages
from django.db import transaction
from rest_framework import serializers


class CustomToRepresentation(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)

        for key, value in data.items():
            try:
                if not value:
                    data[key] = None
            except KeyError:
                pass

        return data


class AdminBase(admin.ModelAdmin):
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        if request.path.endswith("/autocomplete/"):
            queryset = queryset.active().order_by("id")  # type: ignore

        return queryset, use_distinct

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ["created_at", "created_by", "updated_at", "updated_by", "deleted"]

        if obj and obj.deleted:
            return [field.name for field in self.model._meta.get_fields()]

        return readonly_fields

    def has_change_permission(self, request, obj=None):
        if obj and obj.deleted:
            return False

        return super().has_change_permission(request, obj)

    def has_view_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if change:
            obj.updated_by = request.user
        else:
            obj.created_by = request.user
            obj.updated_by = request.user

        return super().save_model(request, obj, form, change)


@transaction.atomic
def admin_action_delete(self, request, queryset, model_name):
    changed = 0

    for instance in queryset:
        if instance.deleted:
            continue

        instance.deleted = True
        instance.updated_by = request.user

        if model_name == "approval chains":
            instance.active = False

        if model_name == "requisitions":
            lines = instance.lines.all()

            for line in lines:
                line.deleted = True
                line.updated_by = request.user

                line.save()

        instance.save()

        changed += 1

    match changed:
        case 0:
            self.message_user(request, f"No {model_name} were eligible.", level=messages.WARNING)
        case _:
            self.message_user(
                request,
                f"The selected {model_name} were soft deleted (total = {changed}).",
                level=messages.SUCCESS,
            )
