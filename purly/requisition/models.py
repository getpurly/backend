from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from purly.address.models import Address
from purly.project.models import Project

from .managers import (
    RequisitionLineManager,
    RequisitionLineManagerActive,
    RequisitionManager,
    RequisitionManagerActive,
)


class CurrencyChoices(models.TextChoices):
    USD = ("usd", "usd")


class StatusChoices(models.TextChoices):
    DRAFT = ("draft", "draft")
    PENDING_APPROVAL = ("pending_approval", "pending approval")
    APPROVED = ("approved", "approved")
    REJECTED = ("rejected", "rejected")


class LineTypeChoices(models.TextChoices):
    GOODS = ("goods", "goods")
    SERVICE = ("service", "service")


class UOMChoices(models.TextChoices):
    EACH = ("each", "each")
    BOX = ("box", "box")


class PaymentTermChoices(models.TextChoices):
    NET30 = ("net_30", "net 30")
    NET45 = ("net_45", "net 45")
    NET90 = ("net_90", "net 90")


class Requisition(models.Model):
    name = models.CharField(max_length=255)
    external_reference = models.CharField(max_length=255, blank=True)
    status = models.CharField(choices=StatusChoices.choices, default=StatusChoices.DRAFT)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="requisitions_owned"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name="project_requisitions",
        blank=True,
        null=True,
    )
    supplier = models.CharField(max_length=255)
    justification = models.TextField()
    total_amount = models.DecimalField(
        max_digits=9, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    currency = models.CharField(choices=CurrencyChoices.choices, default=CurrencyChoices.USD)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="requisitions_created",
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="requisitions_updated",
    )
    submitted_at = models.DateTimeField(blank=True, null=True, editable=False)
    approved_at = models.DateTimeField(blank=True, null=True, editable=False)
    rejected_at = models.DateTimeField(blank=True, null=True, editable=False)
    deleted = models.BooleanField(default=False)

    objects = RequisitionManager()
    objects_active = RequisitionManagerActive()

    class Meta:
        db_table = "requisition"
        verbose_name = "requisition"
        verbose_name_plural = "requisitions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.id} - {self.name}"  # type: ignore


class RequisitionLine(models.Model):
    line_number = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    line_type = models.CharField(choices=LineTypeChoices.choices)
    description = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255, blank=True)
    manufacturer_part_number = models.CharField(max_length=255, blank=True)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)], blank=True, null=True)
    unit_of_measure = models.CharField(choices=UOMChoices.choices, blank=True)
    unit_price = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        blank=True,
        null=True,
    )
    line_total = models.DecimalField(
        max_digits=9, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    payment_term = models.CharField(choices=PaymentTermChoices.choices)
    need_by = models.DateField(blank=True, null=True)
    requisition = models.ForeignKey(Requisition, on_delete=models.CASCADE, related_name="lines")
    ship_to = models.ForeignKey(Address, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="requisition_lines_created",
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="requisition_lines_updated",
    )
    deleted = models.BooleanField(default=False)

    objects = RequisitionLineManager()
    objects_active = RequisitionLineManagerActive()

    class Meta:
        db_table = "requisition_line"
        verbose_name = "requisition line"
        verbose_name_plural = "requisition lines"
        ordering = ["requisition", "line_number"]

    def __str__(self):
        return self.description
