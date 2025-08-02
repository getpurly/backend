from decimal import Decimal

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from purly.requisition.models import Requisition

from .managers import ApprovalChainManager, ApprovalGroupManager, ApprovalManager


class StatusChoices(models.TextChoices):
    PENDING = ("pending", "Pending")
    APPROVED = ("approved", "Approved")
    REJECTED = ("rejected", "Rejected")


class LookupStringChoices(models.TextChoices):
    EXACT = ("exact", "exact")
    IEXACT = ("iexact", "iexact")
    CONTAINS = ("contains", "contains")
    ICONTAINS = ("icontains", "icontains")
    STARTS_WITH = ("startswith", "startswith")
    ISTARTS_WITH = ("istartswith", "istartswith")
    ENDS_WITH = ("endswith", "endswith")
    IENDS_WITH = ("iendswith", "iendswith")
    REGEX = ("regex", "regex")
    IS_NULL = ("is_null", "isnull")


class LookupNumberChoices(models.TextChoices):
    GT = ("gt", "gt")
    GTE = ("gte", "gte")
    LT = ("lt", "lt")
    LTE = ("lte", "lt")


class HeaderFieldChoices(models.TextChoices):
    CURRENCY = ("currency", "Currency")
    EXTERNAL_REFERENCE = ("external_reference", "External Reference")
    JUSTIFICATION = ("justification", "Justification")
    NAME = ("name", "Name")
    OWNER = ("owner", "Owner Username")
    OWNER_EMAIL = ("owner_email", "Owner Email")
    OWNER_FIRST_NAME = ("owner_first_name", "Owner First Name")
    OWNER_LAST_NAME = ("owner_last_name", "Owner Last Name")
    PROJECT = ("project", "Project Name")
    PROJECT_CODE = ("project_code", "Project Code")
    PROJECT_DESCRIPTION = ("project_description", "Project Description")
    SUPPLIER = ("supplier", "Supplier")


class LineFieldStringChoices(models.TextChoices):
    CATEGORY = ("category", "Category")
    DESCRIPTION = ("description", "Description")
    MANUFACTURER = ("manufacturer", "Manufacturer")
    MANUFACTURER_PART_NUMBER = ("manufacturer_part_number", "Manufacturer Part Number")
    NEED_BY = ("need_by", "Need By")
    PAYMENT_TERM = ("payment_term", "Payment Term")
    SHIP_TO_ATTENTION = ("ship_to_attention", "Ship To Attention")
    SHIP_TO_CITY = ("ship_to_city", "Ship To City")
    SHIP_TO_CODE = ("ship_to_code", "Ship To Code")
    SHIP_TO_COUNTRY = ("ship_to_country", "Ship To Country")
    SHIP_TO_NAME = ("ship_to_name", "Ship To Name")
    SHIP_TO_PHONE = ("ship_to_phone", "Ship To Phone")
    SHIP_TO_STATE = ("ship_to_state", "Ship To State")
    SHIP_TO_STREET1 = ("ship_to_street1", "Ship To Street 1")
    SHIP_TO_STREET2 = ("ship_to_street2", "Ship To Street 2")
    SHIP_TO_ZIP = ("ship_to_zip", "Ship To Zip Code")
    UOM = ("uom", "United of Measure")


class LineFieldNumberChoices(models.TextChoices):
    LINE_TOTAL = ("line_total", "Line Total")
    UNIT_PRICE = ("unit_price", "Unit Price")


class LineMatchModeChoices(models.TextChoices):
    ALL = ("all", "all")
    ANY = ("any", "any")


class ApprovalChainModeChoices(models.TextChoices):
    INDIVIDUAL = ("individual", "Individual")
    GROUP = ("group", "Group")


class Approval(models.Model):
    requisition = models.ForeignKey(Requisition, on_delete=models.PROTECT)
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="approvals_as_approver"
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


class ApprovalGroup(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    approver = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="approval_groups",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="approval_groups_created",
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="approval_groups_updated",
    )
    deleted = models.BooleanField(default=False)

    objects = ApprovalGroupManager()

    class Meta:
        db_table = "approval_group"
        verbose_name = "approval group"
        verbose_name_plural = "approval groups"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class ApprovalChain(models.Model):
    name = models.CharField(max_length=255, unique=True)
    approver_mode = models.CharField(choices=ApprovalChainModeChoices, default="individual")
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="approval_chains_as_approver",
        blank=True,
        null=True,
    )
    approver_group = models.ForeignKey(
        ApprovalGroup,
        on_delete=models.PROTECT,
        related_name="approval_chains_as_approver_group",
        blank=True,
        null=True,
    )
    sequence_number = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1000)]
    )
    min_amount = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Minimum amount",
    )
    max_amount = models.DecimalField(
        max_digits=9, decimal_places=2, null=True, blank=True, verbose_name="Maximum amount"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="approval_chains_created",
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="approval_chains_updated"
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


class ApprovalChainHeaderRule(models.Model):
    approval_chain = models.ForeignKey(
        ApprovalChain, on_delete=models.PROTECT, related_name="approval_chain_header_rules"
    )
    field = models.CharField(choices=HeaderFieldChoices)
    lookup = models.CharField(
        choices=list(LookupStringChoices.choices) + list(LookupNumberChoices.choices)
    )
    value = ArrayField(models.CharField(max_length=255), default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="approval_chain_header_rules_created",
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="approval_chain_header_rules_updated",
    )

    class Meta:
        db_table = "approval_chain_header_rule"
        verbose_name = "header rule"
        verbose_name_plural = "header rules"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["field", "lookup", "value"], name="unique_header_rule")
        ]

    def __str__(self):
        value = self.value[0] if len(self.value) == 1 else ", ".join(self.value)

        return f"{self.field} {self.lookup} {value}"


class ApprovalChainLineRule(models.Model):
    approval_chain = models.ForeignKey(
        ApprovalChain, on_delete=models.PROTECT, related_name="approval_chain_line_rules"
    )
    field = models.CharField(
        choices=list(LineFieldStringChoices.choices) + list(LineFieldNumberChoices.choices)
    )
    lookup = models.CharField(
        choices=list(LookupStringChoices.choices) + list(LookupNumberChoices.choices)
    )
    match_mode = models.CharField(choices=LineMatchModeChoices)
    value = ArrayField(models.CharField(max_length=255), default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="approval_chain_line_rules_created",
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="approval_chain_line_rules_updated",
    )

    class Meta:
        db_table = "approval_chain_line_rule"
        verbose_name = "line rule"
        verbose_name_plural = "line rules"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["field", "lookup", "match_mode", "value"], name="unique_line_rule"
            )
        ]

    def __str__(self):
        value = self.value[0] if len(self.value) == 1 else ", ".join(self.value)

        return f"{self.field} {self.lookup} {value}"
