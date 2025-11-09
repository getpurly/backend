from django.conf import settings
from django.db import models

from purly.base import ModelBase

from .managers import AddressManager


class Address(ModelBase):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="addresses_owned"
    )
    name = models.CharField(max_length=255)
    address_code = models.CharField(max_length=255, blank=True)
    description = models.TextField(max_length=2000, blank=True)
    attention = models.CharField(max_length=255)
    phone = models.CharField(max_length=32, blank=True)
    street1 = models.CharField(max_length=255, verbose_name="Street 1")
    street2 = models.CharField(max_length=255, blank=True, verbose_name="Street 2")
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=64)
    zip_code = models.CharField(max_length=64)
    country = models.CharField(max_length=64)
    delivery_instructions = models.TextField(max_length=2000, blank=True)

    objects = AddressManager()

    class Meta(ModelBase.Meta):
        db_table = "address"
        verbose_name = "address"
        verbose_name_plural = "addresses"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.pk} - {self.name}"
