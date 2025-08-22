from django.db import models


class ApprovalQuerySet(models.QuerySet):
    def active(self):
        return self.filter(deleted=False)


class ApprovalManager(models.Manager.from_queryset(ApprovalQuerySet)):
    pass


class ApprovalChainQuerySet(models.QuerySet):
    def active(self):
        return self.filter(deleted=False)


class ApprovalChainManager(models.Manager.from_queryset(ApprovalChainQuerySet)):
    pass


class ApprovalGroupQuerySet(models.QuerySet):
    def active(self):
        return self.filter(deleted=False)


class ApprovalGroupManager(models.Manager.from_queryset(ApprovalGroupQuerySet)):
    pass
