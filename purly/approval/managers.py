from django.db import models


class ApprovalManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)


class ApprovalRuleManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)
