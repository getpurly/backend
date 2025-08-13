from django.db import transaction
from django.http import Http404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, filters, generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.exceptions import BadRequest
from purly.approval.services import (
    cancel_approvals,
    generate_approvals,
    notify_current_sequence,
)

from .filters import REQUISITION_FILTER_FIELDS, REQUISITION_LINE_FILTER_FIELDS
from .models import Requisition, RequisitionLine, RequisitionStatusChoices
from .pagination import RequisitionLinePagination, RequisitionPagination
from .serializers import (
    RequisitionCreateSerializer,
    RequisitionDetailSerializer,
    RequisitionLineListSerializer,
    RequisitionListSerializer,
    RequisitionUpdateSerializer,
)

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
    permission_classes = [IsAuthenticated]
    queryset = Requisition.objects_active.select_related(
        "project", "owner", "created_by", "updated_by"
    )
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

        serializer = self.get_serializer(queryset, many=True)

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

    @transaction.atomic
    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        requisition = self.get_object()

        if requisition.owner != self.request.user:
            raise exceptions.PermissionDenied(
                "You must be the requisition owner to submit for approval."
            )

        if requisition.status != RequisitionStatusChoices.DRAFT:
            raise BadRequest(
                detail="The requisition must be in draft status to submit for approval."
            )

        if generate_approvals(requisition) is False:
            msg = "The requisition cannot be submitted because no approval chains matched."

            raise BadRequest(detail=msg)

        requisition.status = RequisitionStatusChoices.PENDING_APPROVAL
        requisition.submitted_at = timezone.now()
        requisition.rejected_at = None

        requisition.save()

        transaction.on_commit(lambda: notify_current_sequence(requisition))

        serializer = RequisitionDetailSerializer(requisition)

        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=["post"])
    def withdraw(self, request, pk=None):
        requisition = self.get_object()

        if requisition.owner != self.request.user:
            raise exceptions.PermissionDenied(
                "You must be the requisition owner to withdraw from approvals."
            )

        if requisition.status != RequisitionStatusChoices.PENDING_APPROVAL:
            raise BadRequest(
                detail="The requisition must be in pending approval status to withdraw."
            )

        cancel_approvals(requisition)

        requisition.status = RequisitionStatusChoices.DRAFT
        requisition.submitted_at = None

        requisition.save()

        serializer = RequisitionDetailSerializer(requisition)

        return Response(serializer.data)


class RequisitionMineListView(generics.ListAPIView):
    http_method_names = ["get"]
    permission_classes = [IsAuthenticated]
    serializer_class = RequisitionListSerializer
    pagination_class = RequisitionPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = REQUISITION_FILTER_FIELDS
    ordering_fields = REQUISITION_ORDERING

    def get_queryset(self):  # type: ignore
        return Requisition.objects_active.select_related(
            "project", "owner", "created_by", "updated_by"
        ).filter(owner=self.request.user)


class RequisitionLineListView(generics.ListAPIView):
    http_method_names = ["get"]
    permission_classes = [IsAuthenticated]
    queryset = RequisitionLine.objects_active.select_related(
        "ship_to", "ship_to__owner", "ship_to__created_by", "ship_to__updated_by"
    )
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

    def get_queryset(self):  # type: ignore
        return RequisitionLine.objects_active.select_related(
            "ship_to", "ship_to__owner", "ship_to__created_by", "ship_to__updated_by"
        ).filter(requisition__owner=self.request.user)
