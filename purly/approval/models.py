from decimal import Decimal

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from purly.requisition.models import Requisition

from .managers import ApprovalChainManager, ApprovalGroupManager, ApprovalManager


class StatusChoices(models.TextChoices):
    PENDING = ("pending", "pending")
    APPROVED = ("approved", "approved")
    REJECTED = ("rejected", "rejected")
    SKIPPED = ("skipped", "skipped")
    CANCELLED = ("cancelled", "cancelled`")


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
    EQUAL = ("equal", "equal")
    NOT_EQUAL = ("not_equal", "not equal to")
    GT = ("gt", "greater than")
    GTE = ("gte", "greater than, or equal to")
    LT = ("lt", "less than")
    LTE = ("lte", "less than, or equal to")


class HeaderFieldStringChoices(models.TextChoices):
    CURRENCY = ("currency", "currency")
    EXTERNAL_REFERENCE = ("external_reference", "external reference")
    JUSTIFICATION = ("justification", "justification")
    NAME = ("name", "name")
    OWNER = ("owner", "owner username")
    OWNER_EMAIL = ("owner_email", "owner email")
    OWNER_FIRST_NAME = ("owner_first_name", "owner first name")
    OWNER_LAST_NAME = ("owner_last_name", "owner last name")
    PROJECT = ("project", "project name")
    PROJECT_CODE = ("project_code", "project code")
    PROJECT_DESCRIPTION = ("project_description", "project description")
    SUPPLIER = ("supplier", "supplier")


class LineFieldStringChoices(models.TextChoices):
    CATEGORY = ("category", "category")
    DESCRIPTION = ("description", "description")
    MANUFACTURER = ("manufacturer", "manufacturer")
    MANUFACTURER_PART_NUMBER = ("manufacturer_part_number", "manufacturer part number")
    NEED_BY = ("need_by", "need by")
    PAYMENT_TERM = ("payment_term", "payment term")
    SHIP_TO_ATTENTION = ("ship_to_attention", "ship to attention")
    SHIP_TO_CITY = ("ship_to_city", "ship to city")
    SHIP_TO_CODE = ("ship_to_code", "ship to code")
    SHIP_TO_COUNTRY = ("ship_to_country", "ship to country")
    SHIP_TO_NAME = ("ship_to_name", "ship to name")
    SHIP_TO_PHONE = ("ship_to_phone", "ship to phone")
    SHIP_TO_STATE = ("ship_to_state", "ship to state")
    SHIP_TO_STREET1 = ("ship_to_street1", "ship to street 1")
    SHIP_TO_STREET2 = ("ship_to_street2", "ship to street 2")
    SHIP_TO_ZIP = ("ship_to_zip", "ship to zip code")
    UNIT_OF_MEASURE = ("unit_of_measure", "united of measure")


class LineFieldNumberChoices(models.TextChoices):
    LINE_TOTAL = ("line_total", "line total")
    UNIT_PRICE = ("unit_price", "unit price")


class LineMatchModeChoices(models.TextChoices):
    ALL = ("all", "all")
    ANY = ("any", "any")


class ApprovalChainModeChoices(models.TextChoices):
    INDIVIDUAL = ("individual", "individual")
    GROUP = ("group", "group")


class Approval(models.Model):
    requisition = models.ForeignKey(Requisition, on_delete=models.PROTECT, related_name="approvals")
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="approvals_as_approver"
    )
    sequence_number = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1000)]
    )
    status = models.CharField(choices=StatusChoices.choices, default=StatusChoices.PENDING)
    trigger_metadata = models.JSONField(blank=True, null=True)
    system_generated = models.BooleanField()
    notified_at = models.DateTimeField(blank=True, null=True, editable=False)
    approved_at = models.DateTimeField(blank=True, null=True, editable=False)
    rejected_at = models.DateTimeField(blank=True, null=True, editable=False)
    skipped_at = models.DateTimeField(blank=True, null=True, editable=False)
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
    name = models.CharField(
        max_length=255,
        unique=True,
        error_messages={"unique": "This approval group name already exists."},
    )
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
    name = models.CharField(
        max_length=255,
        unique=True,
        error_messages={"unique": "This approval chain name already exists."},
    )
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
    field = models.CharField(choices=HeaderFieldStringChoices)
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
            models.UniqueConstraint(
                fields=["approval_chain", "field", "lookup", "value"],
                name="unique_header_rule",
                violation_error_message="This rule combination already exists for approval chain.",
            )
        ]

    def __str__(self):
        value = self.value[0] if len(self.value) == 1 else ", ".join(self.value)

        field = ""

        if self.field in HeaderFieldStringChoices.values:
            field = HeaderFieldStringChoices(self.field).label

        lookup = ""

        if self.lookup in LookupStringChoices.values:
            lookup = LookupStringChoices(self.lookup).label

        if self.lookup in LookupNumberChoices.values:
            lookup = LookupNumberChoices(self.lookup).label

        return f"For header, {field} field {lookup} {value}"


class ApprovalChainLineRule(models.Model):
    approval_chain = models.ForeignKey(
        ApprovalChain, on_delete=models.PROTECT, related_name="approval_chain_line_rules"
    )
    match_mode = models.CharField(choices=LineMatchModeChoices)
    field = models.CharField(
        choices=list(LineFieldStringChoices.choices) + list(LineFieldNumberChoices.choices)
    )
    lookup = models.CharField(
        choices=list(LookupStringChoices.choices) + list(LookupNumberChoices.choices)
    )
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
                fields=["approval_chain", "match_mode", "field", "lookup", "value"],
                name="unique_line_rule",
                violation_error_message="This rule combination already exists for approval chain.",
            )
        ]

    def __str__(self):
        value = self.value[0] if len(self.value) == 1 else ", ".join(self.value)

        field = ""

        if self.field in HeaderFieldStringChoices.values:
            field = HeaderFieldStringChoices(self.field).label

        if self.field in LineFieldStringChoices.values:
            field = LineFieldStringChoices(self.field).label

        if self.field in LineFieldNumberChoices.values:
            field = LineFieldNumberChoices(self.field).label

        lookup = ""

        if self.lookup in LookupStringChoices.values:
            lookup = LookupStringChoices(self.lookup).label

        if self.lookup in LookupNumberChoices.values:
            lookup = LookupNumberChoices(self.lookup).label

        if self.match_mode == "any":
            return f"For {self.match_mode} line, {field} field {lookup} {value}"

        return f"For {self.match_mode} lines, {field} field {lookup} {value}"
