from django.conf import settings
from django.contrib import admin, messages
from django.db import models
from django.http import HttpResponseRedirect
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

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):  # type: ignore
        obj = self.get_object(request, object_id) if object_id else None

        if request.method == "POST" and obj and obj.deleted:
            self.message_user(request, "This record has been deleted.", level=messages.WARNING)

            return HttpResponseRedirect(request.path)

        return super().changeform_view(request, object_id, form_url, extra_context)

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


class ModelBase(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_created",
        null=True,
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_updated",
        null=True,
    )
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True
