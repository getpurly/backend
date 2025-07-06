from django.conf import settings
from django.db import models

from .managers import AddressManager


class Address(models.Model):
    name = models.CharField(max_length=255)
    address_code = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    attention = models.CharField(max_length=255)
    phone = models.CharField(max_length=32, blank=True)
    street1 = models.CharField(max_length=255)
    street2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=64)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=64)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="addresses_owned"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="addresses_created",
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="addresses_updated",
    )
    deleted = models.BooleanField(default=False)

    objects = AddressManager()

    class Meta:
        db_table = "address"
        verbose_name = "address"
        verbose_name_plural = "addresses"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
