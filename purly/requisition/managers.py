from django.db import models


class RequisitionQuerySet(models.QuerySet):
    def active(self):
        return self.filter(deleted=False)


class RequisitionManager(models.Manager.from_queryset(RequisitionQuerySet)):
    pass


class RequisitionLineQuerySet(models.QuerySet):
    def active(self):
        return self


class RequisitionLineManager(models.Manager.from_queryset(RequisitionLineQuerySet)):
    pass
