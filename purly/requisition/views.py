from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, filters, generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import REQUISITION_FILTER_FIELDS, REQUISITION_LINE_FILTER_FIELDS
from .models import Requisition, RequisitionLine
from .pagination import RequisitionLinePagination, RequisitionPagination
from .serializers import (
    RequisitionCreateSerializer,
    RequisitionDetailSerializer,
    RequisitionLineListSerializer,
    RequisitionListSerializer,
    RequisitionUpdateSerializer,
)

REQUISITION_ORDERING = ["total_amount", "created_at", "updated_at", "submitted_at", "approved_at"]
REQUISITION_LINE_ORDERING = ["line_total", "need_by", "created_at", "updated_at"]


class RequisitionViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "put"]
    permission_classes = [IsAuthenticated]
    queryset = Requisition.objects.select_related(
        "project", "owner", "created_by", "updated_by"
    ).all()
    serializer_class = RequisitionListSerializer
    pagination_class = RequisitionPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = REQUISITION_FILTER_FIELDS
    ordering_fields = REQUISITION_ORDERING

    def get_object(self):
        try:
            return super().get_object()
        except Http404 as exc:
            raise exceptions.NotFound(detail="No requisition matches the given query.") from exc

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = RequisitionListSerializer(page, many=True)

            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(self.get_queryset(), many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = RequisitionCreateSerializer(
            data=request.data, context=self.get_serializer_context()
        )

        serializer.is_valid(raise_exception=True)

        obj = serializer.save()

        requisition_detail = RequisitionDetailSerializer(
            obj, context=self.get_serializer_context()
        ).data

        return Response(requisition_detail, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        requisition = self.get_object()
        serializer = RequisitionDetailSerializer(requisition)

        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        requisition = self.get_object()
        serializer = RequisitionUpdateSerializer(requisition, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        obj = serializer.save(updated_by=self.request.user)
        requisition_detail = RequisitionDetailSerializer(
            obj, context=self.get_serializer_context()
        ).data

        return Response(requisition_detail, status=status.HTTP_200_OK)


class RequisitionMineListView(generics.ListAPIView):
    http_method_names = ["get"]
    permission_classes = [IsAuthenticated]
    serializer_class = RequisitionListSerializer
    pagination_class = RequisitionPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = REQUISITION_FILTER_FIELDS
    ordering_fields = REQUISITION_ORDERING

    def get_queryset(self): # type: ignore
        return Requisition.objects.select_related(
            "project", "owner", "created_by", "updated_by"
        ).filter(owner=self.request.user)


class RequisitionLineListView(generics.ListAPIView):
    http_method_names = ["get"]
    permission_classes = [IsAuthenticated]
    queryset = RequisitionLine.objects.select_related(
        "ship_to", "ship_to__owner", "ship_to__created_by", "ship_to__updated_by"
    ).all()
    serializer_class = RequisitionLineListSerializer
    pagination_class = RequisitionLinePagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = REQUISITION_LINE_FILTER_FIELDS
    ordering_fields = REQUISITION_LINE_ORDERING


class RequisitionLineMineListView(generics.ListAPIView):
    http_method_names = ["get"]
    permission_classes = [IsAuthenticated]
    serializer_class = RequisitionLineListSerializer
    pagination_class = RequisitionLinePagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = REQUISITION_LINE_FILTER_FIELDS
    ordering_fields = REQUISITION_LINE_ORDERING

    def get_queryset(self): # type: ignore
        return RequisitionLine.objects.select_related(
            "ship_to", "ship_to__owner", "ship_to__created_by", "ship_to__updated_by"
        ).filter(requisition__owner=self.request.user)
