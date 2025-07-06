from rest_framework import serializers

from purly.user.serializers import UserDetailSerializer
from purly.utils import CustomToRepresentation

from .models import Project


class ProjectDetailSerializer(CustomToRepresentation, serializers.ModelSerializer):
    created_by = UserDetailSerializer(read_only=True)
    updated_by = UserDetailSerializer(read_only=True)
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


class ProjectListSerializer(CustomToRepresentation, serializers.ModelSerializer):
    created_by = UserDetailSerializer(read_only=True)
    updated_by = UserDetailSerializer(read_only=True)

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
