from django.db import models

from purly.base import ModelBase

from .managers import ProjectManager


class Project(ModelBase):
    name = models.CharField(
        max_length=255,
        unique=True,
        error_messages={"unique": "This project name already exists."},
    )
    project_code = models.CharField(max_length=64, blank=True)
    description = models.TextField(max_length=2000)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    objects = ProjectManager()

    class Meta(ModelBase.Meta):
        db_table = "project"
        verbose_name = "project"
        verbose_name_plural = "projects"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.pk} - {self.name}"
