from django.conf import settings
from django.db import models

from .managers import ProjectManager, ProjectManagerActive


class Project(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        error_messages={"unique": "This project name already exists."},
    )
    project_code = models.CharField(max_length=64, blank=True)
    description = models.TextField()
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="projects_created",
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="projects_updated",
    )
    deleted = models.BooleanField(default=False)

    objects = ProjectManager()
    objects_active = ProjectManagerActive()

    class Meta:
        db_table = "project"
        verbose_name = "project"
        verbose_name_plural = "projects"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.id} - {self.name}"  # type: ignore
