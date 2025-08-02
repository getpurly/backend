from django.db import models


class ApprovalManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()


class ApprovalChainManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()


class ApprovalGroupManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()
