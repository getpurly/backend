from django.db import models


class ProjectQuerySet(models.QuerySet):
    def active(self):
        return self.filter(deleted=False)


class ProjectManager(models.Manager.from_queryset(ProjectQuerySet)):
    pass
