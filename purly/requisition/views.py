from django.db import transaction
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import exceptions, filters, generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from purly.permissions import IsOwnerOrAdmin

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
from .services import on_submit, on_withdraw, submit_withdraw_validation

REQUISITION_ORDERING = [
    "total_amount",
    "created_at",
    "updated_at",
    "submitted_at",
    "approved_at",
    "rejected_at",
]
REQUISITION_LINE_ORDERING = ["line_total", "need_by", "created_at", "updated_at"]


class RequisitionViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "put"]
    permission_classes = [IsOwnerOrAdmin]
    queryset = (
        Requisition.objects.active()  # type: ignore
        .select_related("project", "owner", "created_by", "updated_by")
        .prefetch_related("lines")
    )
    pagination_class = RequisitionPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = REQUISITION_FILTER_FIELDS
    ordering_fields = REQUISITION_ORDERING

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return self.queryset

        return self.queryset.filter(owner=user)

    def get_object(self):
        try:
            return super().get_object()
        except Http404 as exc:
            raise exceptions.NotFound(detail="No requisition matches the given query.") from exc

    @extend_schema(summary="List requisitions", request=None, responses=RequisitionListSerializer)
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = RequisitionListSerializer(page, many=True)

            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    @extend_schema(
        summary="Create requisition",
        request=RequisitionCreateSerializer,
        responses=RequisitionDetailSerializer,
    )
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

    @extend_schema(
        summary="Retrieve requisition", request=None, responses=RequisitionDetailSerializer
    )
    def retrieve(self, request, *args, **kwargs):
        requisition = self.get_object()
        serializer = RequisitionDetailSerializer(requisition)

        return Response(serializer.data)

    @extend_schema(
        summary="Update requisition",
        request=RequisitionUpdateSerializer,
        responses=RequisitionDetailSerializer,
    )
    def update(self, request, *args, **kwargs):
        requisition = self.get_object()
        serializer = RequisitionUpdateSerializer(requisition, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        obj = serializer.save(updated_by=self.request.user)
        requisition_detail = RequisitionDetailSerializer(
            obj, context=self.get_serializer_context()
        ).data

        return Response(requisition_detail, status=status.HTTP_200_OK)

    @extend_schema(summary="Submit", request=None, responses=RequisitionDetailSerializer)
    @transaction.atomic
    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        requisition = self.get_object()

        submit_withdraw_validation(self.request.user, requisition, "submit")

        obj = on_submit(requisition, request_user=request.user)
        serializer = RequisitionDetailSerializer(obj)

        return Response(serializer.data)

    @extend_schema(summary="Withdraw", request=None, responses=RequisitionDetailSerializer)
    @transaction.atomic
    @action(detail=True, methods=["post"], serializer_class=RequisitionDetailSerializer)
    def withdraw(self, request, pk=None):
        requisition = self.get_object()

        submit_withdraw_validation(self.request.user, requisition, "withdraw")

        obj = on_withdraw(requisition, request_user=request.user)
        serializer = RequisitionDetailSerializer(obj)

        return Response(serializer.data)


@extend_schema(
    summary="List requisitions owned by the current user",
    request=None,
    responses=RequisitionListSerializer,
)
class RequisitionMineListView(generics.ListAPIView):
    http_method_names = ["get"]
    permission_classes = [IsAuthenticated]
    serializer_class = RequisitionListSerializer
    pagination_class = RequisitionPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = REQUISITION_FILTER_FIELDS
    ordering_fields = REQUISITION_ORDERING

    def get_queryset(self):
        return (
            Requisition.objects.active()  # type: ignore
            .select_related("project", "owner", "created_by", "updated_by")
            .prefetch_related("lines")
            .filter(owner=self.request.user)
        )


@extend_schema(
    summary="List requisition lines", request=None, responses=RequisitionLineListSerializer
)
class RequisitionLineListView(generics.ListAPIView):
    http_method_names = ["get"]
    permission_classes = [IsOwnerOrAdmin]
    queryset = RequisitionLine.objects.active().select_related(  # type: ignore
        "ship_to", "created_by", "updated_by"
    )
    serializer_class = RequisitionLineListSerializer
    pagination_class = RequisitionLinePagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = REQUISITION_LINE_FILTER_FIELDS
    ordering_fields = REQUISITION_LINE_ORDERING

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return self.queryset

        return self.queryset.filter(requisition__owner=user)


@extend_schema(
    summary="List requisition lines owned by the current user",
    request=None,
    responses=RequisitionListSerializer,
)
class RequisitionLineMineListView(generics.ListAPIView):
    http_method_names = ["get"]
    permission_classes = [IsAuthenticated]
    serializer_class = RequisitionLineListSerializer
    pagination_class = RequisitionLinePagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = REQUISITION_LINE_FILTER_FIELDS
    ordering_fields = REQUISITION_LINE_ORDERING

    def get_queryset(self):
        return (
            RequisitionLine.objects.active()  # type: ignore
            .select_related("ship_to", "created_by", "updated_by")
            .filter(requisition__owner=self.request.user)
        )
