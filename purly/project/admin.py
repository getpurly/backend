from django.contrib import admin

from .forms import ProjectForm
from .models import Project


class ProjectAdmin(admin.ModelAdmin):
    form = ProjectForm
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
    list_filter = [
        "start_date",
        "end_date",
        "created_at",
        "updated_at",
    ]
    search_fields = [
        "name",
        "project_code",
        "description",
        "created_by__username",
        "updated_by__username",
    ]
    readonly_fields = ["created_at", "created_by", "updated_at", "updated_by"]

    def save_model(self, request, obj, form, change):
        if change:
            obj.updated_by = request.user
        else:
            obj.created_by = request.user
            obj.updated_by = request.user

        return super().save_model(request, obj, form, change)


admin.site.register(Project, ProjectAdmin)
