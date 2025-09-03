from django.db import models
from django.db.models import Q
from django.utils import timezone

now = timezone.now().date()


class ApprovalQuerySet(models.QuerySet):
    def active(self):
        return self.filter(deleted=False)


class ApprovalManager(models.Manager.from_queryset(ApprovalQuerySet)):
    pass


class ApprovalChainQuerySet(models.QuerySet):
    def active(self):
        return self.filter(deleted=False)

    def current(self):
        return (
            self.active()
            .filter(Q(valid_from__isnull=True) | Q(valid_from__lte=now))
            .filter(Q(valid_to__isnull=True) | Q(valid_to__gte=now))
            .filter(active=True)
        )


class ApprovalChainManager(models.Manager.from_queryset(ApprovalChainQuerySet)):
    pass


class ApprovalGroupQuerySet(models.QuerySet):
    def active(self):
        return self.filter(deleted=False)


class ApprovalGroupManager(models.Manager.from_queryset(ApprovalGroupQuerySet)):
    pass
