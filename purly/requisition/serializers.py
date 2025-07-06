from datetime import UTC, datetime
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from rest_framework import serializers

from purly.address.serializers import AddressDetailSerializer
from purly.project.serializers import ProjectListSerializer
from purly.user.serializers import UserDetailSerializer
from purly.utils import CustomToRepresentation

from .models import (
    CurrencyChoices,
    LineTypeChoices,
    PaymentTermChoices,
    Requisition,
    RequisitionLine,
    StatusChoices,
    UOMChoices,
)


class RequisitionLineListSerializer(CustomToRepresentation, serializers.ModelSerializer):
    ship_to = AddressDetailSerializer()
    created_by = UserDetailSerializer(read_only=True)
    updated_by = UserDetailSerializer(read_only=True)

    class Meta:
        model = RequisitionLine
        fields = [
            "id",
            "line_number",
            "line_type",
            "description",
            "category",
            "manufacturer",
            "manufacturer_part_number",
            "quantity",
            "uom",
            "unit_price",
            "line_total",
            "payment_term",
            "need_by",
            "requisition",
            "ship_to",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]


class RequisitionLineDetailSerializer(CustomToRepresentation, serializers.ModelSerializer):
    ship_to = AddressDetailSerializer()
    created_by = UserDetailSerializer(read_only=True)
    updated_by = UserDetailSerializer(read_only=True)

    class Meta:
        model = RequisitionLine
        fields = [
            "id",
            "line_number",
            "line_type",
            "description",
            "category",
            "manufacturer",
            "manufacturer_part_number",
            "quantity",
            "uom",
            "unit_price",
            "line_total",
            "payment_term",
            "need_by",
            "ship_to",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]


class RequisitionLineCreateSerializer(serializers.ModelSerializer):
    line_type = serializers.CharField()
    uom = serializers.CharField(allow_blank=True, required=False)
    payment_term = serializers.CharField()

    class Meta:
        model = RequisitionLine
        fields = [
            "line_number",
            "line_type",
            "description",
            "category",
            "manufacturer",
            "manufacturer_part_number",
            "quantity",
            "uom",
            "unit_price",
            "line_total",
            "payment_term",
            "need_by",
            "ship_to",
        ]
        extra_kwargs = {
            "ship_to": {
                "error_messages": {
                    "does_not_exist": "This address does not exist: {pk_value}",
                }
            }
        }

    def validate_line_type(self, value):
        if value not in LineTypeChoices.values:
            raise serializers.ValidationError(f"This is not a valid line type: {value}")

        return value

    def validate_uom(self, value):
        if value != "" and value not in UOMChoices.values:
            raise serializers.ValidationError(f"This is not a valid unit of measure: {value}")

        return value

    def validate_payment_term(self, value):
        if value not in PaymentTermChoices.values:
            raise serializers.ValidationError(f"This is not a valid payment term: {value}")

        return value

    def validate_need_by(self, value):
        now = datetime.now(UTC).date()

        if value < now:
            raise serializers.ValidationError(f"This value must be a future date: {value}")

        return value

    def validate(self, attrs):
        line_number = attrs.get("line_number", 0)
        line_type = attrs.get("line_type", "")
        quantity = attrs.get("quantity", 0)
        unit_price = attrs.get("unit_price", Decimal("0.00"))
        uom = attrs.get("uom", "")
        line_total = attrs.get("line_total", Decimal("0.00"))

        if line_type == "service":
            if any([quantity, unit_price, uom]):
                raise serializers.ValidationError(
                    f"Line {line_number} marked as service; quantity, unit price, and unit of measure fields must be unset or excluded."  # noqa: E501
                )
        else:
            if not all([quantity, unit_price, uom]):
                raise serializers.ValidationError(
                    f"Line {line_number} marked as goods; quantity, unit price, and unit of measure fields must be included and set."  # noqa: E501
                )

            calculated_line_total = quantity * unit_price

            if line_total != calculated_line_total:
                raise serializers.ValidationError(
                    {"line_total": "This value does not align with unit price and quantity."}
                )

        return attrs


class RequisitionListSerializer(CustomToRepresentation, serializers.ModelSerializer):
    owner = UserDetailSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)
    created_by = UserDetailSerializer(read_only=True)
    updated_by = UserDetailSerializer(read_only=True)

    class Meta:
        model = Requisition
        fields = [
            "id",
            "name",
            "external_reference",
            "status",
            "owner",
            "project",
            "supplier",
            "justification",
            "total_amount",
            "currency",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
            "submitted_at",
            "approved_at",
        ]


class RequisitionDetailSerializer(CustomToRepresentation, serializers.ModelSerializer):
    owner = UserDetailSerializer(read_only=True)
    project = ProjectListSerializer(read_only=True)
    created_by = UserDetailSerializer(read_only=True)
    updated_by = UserDetailSerializer(read_only=True)
    lines = serializers.SerializerMethodField()

    class Meta:
        model = Requisition
        fields = [
            "id",
            "name",
            "external_reference",
            "status",
            "owner",
            "project",
            "supplier",
            "justification",
            "total_amount",
            "currency",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
            "submitted_at",
            "approved_at",
            "lines",
        ]

    def get_lines(self, obj):
        lines = obj.lines.order_by("line_number")

        return RequisitionLineDetailSerializer(lines, many=True).data


class RequisitionCreateSerializer(serializers.ModelSerializer):
    status = serializers.CharField()
    currency = serializers.CharField()
    lines = RequisitionLineCreateSerializer(many=True)

    class Meta:
        model = Requisition
        fields = [
            "name",
            "external_reference",
            "status",
            "owner",
            "project",
            "supplier",
            "justification",
            "total_amount",
            "currency",
            "lines",
        ]
        extra_kwargs = {
            "user": {
                "error_messages": {
                    "does_not_exist": "This user does not exist: {pk_value}",
                }
            },
            "project": {
                "error_messages": {
                    "does_not_exist": "This project does not exist: {pk_value}",
                }
            },
        }

    def validate_status(self, value):
        if value not in StatusChoices.values:
            raise serializers.ValidationError(f"This is not a valid status: {value}")

        return value

    def validate_currency(self, value):
        if value not in CurrencyChoices.values:
            raise serializers.ValidationError(f"This is not a valid currency: {value}")

        return value

    def validate(self, attrs):
        total_amount = attrs.get("total_amount", Decimal("0.00"))
        lines = attrs.get("lines", [])

        if len(lines) == 0:
            raise serializers.ValidationError({"lines": "Ensure at least one line is provided."})

        if len(lines) >= settings.MAX_REQUISITION_LINES:
            raise serializers.ValidationError(
                {"lines": "Ensure only 250 or less lines are provided."}
            )

        line_numbers = [line["line_number"] for line in lines]

        if len(line_numbers) > len(set(line_numbers)):
            raise serializers.ValidationError({"lines": "Line numbers must contain unique values."})

        line_totals = [line["line_total"] for line in lines]

        if total_amount != sum(line_totals, Decimal("0.00")):
            raise serializers.ValidationError(
                {"total_amount": "This value does not align with line total(s)."}
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        lines = validated_data.pop("lines")
        requisition = Requisition.objects.create(created_by=user, updated_by=user, **validated_data)

        for line in lines:
            RequisitionLine.objects.create(
                requisition=requisition, created_by=user, updated_by=user, **line
            )

        return requisition
