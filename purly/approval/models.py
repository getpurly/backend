from decimal import Decimal

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from purly.requisition.models import Requisition

from .managers import ApprovalChainManager, ApprovalManager


class StatusChoices(models.TextChoices):
    PENDING = ("pending", "Pending")
    APPROVED = ("approved", "Approved")
    REJECTED = ("rejected", "Rejected")


class Approval(models.Model):
    requisition = models.ForeignKey(Requisition, on_delete=models.PROTECT)
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="approval_approver"
    )
    sequence_number = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1000)]
    )
    status = models.CharField(choices=StatusChoices.choices, default=StatusChoices.PENDING)
    notified_at = models.DateTimeField(blank=True, null=True, editable=False)
    approved_at = models.DateTimeField(blank=True, null=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="approvals_created",
        null=True,
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="approvals_updated",
        null=True,
    )
    deleted = models.BooleanField(default=False)

    objects = ApprovalManager()

    class Meta:
        db_table = "approval"
        verbose_name = "approval"
        verbose_name_plural = "approvals"
        ordering = ["-created_at"]

    def __str__(self):
        return self.requisition.name


class ApprovalChain(models.Model):
    name = models.CharField(max_length=255)
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="approval_rules_approver"
    )
    sequence_number = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1000)]
    )
    external_reference = ArrayField(models.CharField(max_length=255), blank=True, default=list)
    owner = ArrayField(models.CharField(max_length=255), blank=True, default=list)
    project = ArrayField(models.CharField(max_length=255), blank=True, default=list)
    supplier = ArrayField(models.CharField(max_length=255), blank=True, default=list)
    min_amount = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Minimum amount",
    )
    max_amount = models.DecimalField(
        max_digits=9, decimal_places=2, null=True, blank=True, verbose_name="Maximum amount"
    )
    currency = ArrayField(models.CharField(max_length=255), blank=True, default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="approval_rules_created",
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="approval_rules_updated"
    )
    active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)

    objects = ApprovalChainManager()

    class Meta:
        db_table = "approval_chain"
        verbose_name = "approval chain"
        verbose_name_plural = "approval chains"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
