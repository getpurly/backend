from django.contrib import admin

from purly.base import AdminBase
from purly.utils import admin_action_delete

from .forms import ProjectForm
from .models import Project


class ProjectAdmin(AdminBase):
    actions = ["delete"]
    form = ProjectForm
    fieldsets = (
        (
            "Basic Settings",
            {
                "fields": ("name",),
            },
        ),
        (
            "Project Information",
            {
                "fields": ("project_code", "description", "start_date", "end_date"),
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
    list_filter = ["start_date", "end_date", "created_at", "updated_at", "deleted"]
    search_fields = [
        "id",
        "name",
        "project_code",
        "description",
        "created_by__username",
        "updated_by__username",
    ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        return queryset.select_related("created_by", "updated_by")

    @admin.action(description="Soft delete selected projects")
    def delete(self, request, queryset):
        admin_action_delete(self, request, queryset, "projects")


admin.site.register(Project, ProjectAdmin)
