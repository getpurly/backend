from rest_framework import serializers

from purly.base import CustomToRepresentation
from purly.user.serializers import UserSimpleDetailSerializer

from .models import Approval


class ApprovalListSerializer(CustomToRepresentation, serializers.ModelSerializer):
    approver = UserSimpleDetailSerializer(read_only=True)
    created_by = UserSimpleDetailSerializer(read_only=True)
    updated_by = UserSimpleDetailSerializer(read_only=True)

    class Meta:
        model = Approval
        fields = [
            "id",
            "approver",
            "sequence_number",
            "status",
            "comment",
            "notified_at",
            "approved_at",
            "rejected_at",
            "skipped_at",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]


class ApprovalDetailSerializer(CustomToRepresentation, serializers.ModelSerializer):
    approver = UserSimpleDetailSerializer(read_only=True)
    created_by = UserSimpleDetailSerializer(read_only=True)
    updated_by = UserSimpleDetailSerializer(read_only=True)

    class Meta:
        model = Approval
        fields = [
            "id",
            "approver",
            "sequence_number",
            "status",
            "comment",
            "rule_metadata",
            "system_generated",
            "notified_at",
            "approved_at",
            "rejected_at",
            "skipped_at",
            "requisition",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]


class ApprovalRequestSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = Approval
        fields = ["comment"]
