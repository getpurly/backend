from django.contrib import admin

from .forms import ProjectForm
from .models import Project


class ProjectAdmin(admin.ModelAdmin):
    form = ProjectForm
    fields = [
        "name",
        "project_code",
        "description",
        "start_date",
        "end_date",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
        "deleted",
    ]
    list_display = [
        "id",
        "name",
        "project_code",
        "description",
        "start_date",
        "end_date",
        "created_at",
        "created_by",
        "updated_at",
        "updated_by",
    ]
    list_filter = ["start_date", "end_date", "created_at", "updated_at", "deleted"]
    search_fields = [
        "id",
        "name",
        "project_code",
        "description",
        "created_by__username",
        "updated_by__username",
    ]

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        if request.path.endswith("/autocomplete/"):
            queryset = queryset.active().order_by("id")  # type: ignore

        return queryset, use_distinct

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ["created_at", "created_by", "updated_at", "updated_by"]

        if obj is None:
            return [*readonly_fields, "deleted"]

        return readonly_fields

    def save_model(self, request, obj, form, change):
        if change:
            obj.updated_by = request.user
        else:
            obj.created_by = request.user
            obj.updated_by = request.user

        return super().save_model(request, obj, form, change)


admin.site.register(Project, ProjectAdmin)
