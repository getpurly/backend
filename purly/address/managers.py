from django.db import models


class AddressManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()


class AddressManagerActive(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)
