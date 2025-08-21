from django.db import models


class RequisitionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def active(self):
        return self.get_queryset().filter(deleted=False)


class RequisitionLineManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def active(self):
        return self.get_queryset().filter(deleted=False)
