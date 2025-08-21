from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import exceptions, filters, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import PROJECT_FILTER_FIELDS
from .models import Project
from .pagination import ProjectPagination
from .serializers import (
    ProjectCreateSerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
    ProjectUpdateSerializer,
)


class ProjectViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "put"]
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.active().select_related("created_by", "updated_by")  # type: ignore
    serializer_class = ProjectListSerializer
    pagination_class = ProjectPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = PROJECT_FILTER_FIELDS
    ordering_fields = ["start_date", "end_date", "created_at", "updated_at"]

    def get_object(self):
        try:
            return super().get_object()
        except Http404 as exc:
            raise exceptions.NotFound(detail="No project matches the given query.") from exc

    @extend_schema(summary="List projects", request=None, responses=ProjectListSerializer)
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = ProjectListSerializer(page, many=True)

            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    @extend_schema(
        summary="Create project", request=ProjectCreateSerializer, responses=ProjectDetailSerializer
    )
    def create(self, request, *args, **kwargs):
        serializer = ProjectCreateSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        obj = serializer.save(created_by=self.request.user, updated_by=self.request.user)
        project_detail = ProjectDetailSerializer(obj, context=self.get_serializer_context()).data

        return Response(project_detail, status=status.HTTP_201_CREATED)

    @extend_schema(summary="Retrieve project", request=None, responses=ProjectDetailSerializer)
    def retrieve(self, request, *args, **kwargs):
        project = self.get_object()
        serializer = ProjectDetailSerializer(project)

        return Response(serializer.data)

    @extend_schema(
        summary="Update project", request=ProjectUpdateSerializer, responses=ProjectDetailSerializer
    )
    def update(self, request, *args, **kwargs):
        project = self.get_object()
        serializer = ProjectUpdateSerializer(project, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        obj = serializer.save(updated_by=self.request.user)
        project_detail = ProjectDetailSerializer(obj, context=self.get_serializer_context()).data

        return Response(project_detail, status=status.HTTP_200_OK)
