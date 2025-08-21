from django.db import models


class ApprovalManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def active(self):
        return self.get_queryset().filter(deleted=False)


class ApprovalChainManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def active(self):
        return self.get_queryset().filter(deleted=False)


class ApprovalGroupManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def active(self):
        return self.get_queryset().filter(deleted=False)
