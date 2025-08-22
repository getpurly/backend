from django.db import models


class AddressQuerySet(models.QuerySet):
    def active(self):
        return self.filter(deleted=False)


class AddressManager(models.Manager.from_queryset(AddressQuerySet)):
    pass
