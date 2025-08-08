from django.utils import timezone
from rest_framework import serializers

from purly.user.serializers import UserDetailSerializer
from purly.utils import CustomToRepresentation

from .models import Approval, StatusChoices


class ApprovalDetailSerializer(CustomToRepresentation, serializers.ModelSerializer):
    approver = UserDetailSerializer(read_only=True)
    created_by = UserDetailSerializer(read_only=True)
    updated_by = UserDetailSerializer(read_only=True)

    class Meta:
        model = Approval
        fields = [
            "id",
            "approver",
            "sequence_number",
            "status",
            "comment",
            "trigger_metadata",
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


class ApprovalListSerializer(CustomToRepresentation, serializers.ModelSerializer):
    approver = UserDetailSerializer(read_only=True)
    created_by = UserDetailSerializer(read_only=True)
    updated_by = UserDetailSerializer(read_only=True)

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


class ApprovalSubmitSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = Approval
        fields = ["comment"]

    def update(self, instance, validated_data):
        instance.status = StatusChoices.APPROVED

        if "comment" in validated_data:
            instance.comment = validated_data["comment"]

        instance.approved_at = timezone.now()
        instance.updated_by = validated_data["updated_by"]

        instance.save()

        return instance


class ApprovalRejectSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = Approval
        fields = ["comment"]

    def update(self, instance, validated_data):
        instance.status = StatusChoices.REJECTED

        if "comment" in validated_data:
            instance.comment = validated_data["comment"]

        instance.rejected_at = timezone.now()
        instance.updated_by = validated_data["updated_by"]

        instance.save()

        return instance
