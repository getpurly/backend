from rest_framework import serializers

from purly.base import CustomToRepresentation
from purly.user.serializers import UserSimpleDetailSerializer

from .models import Project


class ProjectListSerializer(CustomToRepresentation, serializers.ModelSerializer):
    created_by = UserSimpleDetailSerializer(read_only=True)
    updated_by = UserSimpleDetailSerializer(read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "project_code",
            "description",
            "start_date",
            "end_date",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]


class ProjectDetailSerializer(CustomToRepresentation, serializers.ModelSerializer):
    created_by = UserSimpleDetailSerializer(read_only=True)
    updated_by = UserSimpleDetailSerializer(read_only=True)
    requisitions = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True, source="project_requisitions"
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "project_code",
            "description",
            "start_date",
            "end_date",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
            "requisitions",
        ]


class ProjectSimpleDetailSerializer(CustomToRepresentation, serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "id",
            "name",
        ]


class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "name",
            "project_code",
            "description",
            "start_date",
            "end_date",
        ]

    def validate(self, attrs):
        start_date = attrs.get("start_date", "")
        end_date = attrs.get("end_date", "")

        if start_date > end_date:
            raise serializers.ValidationError("The end date must be after start date.")

        return attrs


class ProjectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "name",
            "project_code",
            "description",
            "start_date",
            "end_date",
        ]
