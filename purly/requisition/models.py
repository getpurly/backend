from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from purly.address.models import Address
from purly.project.models import Project

from .managers import RequisitionLineManager, RequisitionManager


class CurrencyChoices(models.TextChoices):
    USD = ("usd", "USD")


class StatusChoices(models.TextChoices):
    PENDING_APPROVAL = ("pending_approval", "Pending Approval")
    APPROVED = ("approved", "Approved")
    REJECTED = ("rejected", "Rejected")


class LineTypeChoices(models.TextChoices):
    GOODS = ("goods", "Goods")
    SERVICE = ("service", "Service")


class UOMChoices(models.TextChoices):
    EACH = ("each", "Each")
    BOX = ("box", "Box")


class PaymentTermChoices(models.TextChoices):
    NET30 = ("net_30", "Net 30")
    NET45 = ("net_45", "Net 45")
    NET90 = ("net_90", "Net 90")


class Requisition(models.Model):
    name = models.CharField(max_length=255)
    external_reference = models.CharField(max_length=255, blank=True)
    status = models.CharField(choices=StatusChoices.choices, default=StatusChoices.PENDING_APPROVAL)
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
    deleted = models.BooleanField(default=False)

    objects = RequisitionManager()

    class Meta:
        db_table = "requisition"
        verbose_name = "requisition"
        verbose_name_plural = "requisitions"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class RequisitionLine(models.Model):
    line_number = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    line_type = models.CharField(choices=LineTypeChoices.choices)
    description = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255, blank=True)
    manufacturer_part_number = models.CharField(max_length=255, blank=True)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)], blank=True, null=True)
    uom = models.CharField(choices=UOMChoices.choices, blank=True)
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

    class Meta:
        db_table = "requisition_line"
        verbose_name = "requisition line"
        verbose_name_plural = "requisition lines"
        ordering = ["requisition", "line_number"]

    def __str__(self):
        return self.description
