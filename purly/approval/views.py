from django.db import transaction
from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import exceptions, generics, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from purly.permissions import IsOwnerOrAdmin

from .models import Approval, ApprovalStatusChoices
from .pagination import ApprovalPagination
from .serializers import (
    ApprovalDetailSerializer,
    ApprovalListSerializer,
    ApprovalRequestSerializer,
)
from .services import (
    approval_request_validation,
    on_approve_skip,
    on_reject,
)


class ApprovalViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    http_method_names = ["get", "post"]
    permission_classes = [IsOwnerOrAdmin]
    queryset = Approval.objects.active().select_related("approver", "created_by", "updated_by")  # type: ignore
    serializer_class = ApprovalListSerializer
    pagination_class = ApprovalPagination
    ordering_fields = ["created_at", "updated_at"]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            return self.queryset

        return self.queryset.filter(approver=user)

    def get_object(self):
        try:
            return super().get_object()
        except Http404 as exc:
            raise exceptions.NotFound(detail="No approval matches the given query.") from exc

    @extend_schema(summary="List approvals", request=None, responses=ApprovalListSerializer)
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = ApprovalListSerializer(page, many=True)

            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    @extend_schema(summary="Retrieve approval", request=None, responses=ApprovalDetailSerializer)
    def retrieve(self, request, *args, **kwargs):
        approval = self.get_object()
        serializer = ApprovalDetailSerializer(approval)

        return Response(serializer.data)

    @extend_schema(
        summary="Approve",
        request=ApprovalRequestSerializer,
        responses=ApprovalDetailSerializer,
    )
    @transaction.atomic
    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        approval = self.get_object()

        approval_request_validation(self.request.user, "approve", approval)

        serializer = ApprovalRequestSerializer(approval, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        obj = on_approve_skip(approval, approval.requisition, "approve", request_user=request.user)
        approval_detail = ApprovalDetailSerializer(obj, context=self.get_serializer_context()).data

        return Response(approval_detail)

    @extend_schema(
        summary="Reject",
        request=ApprovalRequestSerializer,
        responses=ApprovalDetailSerializer,
    )
    @transaction.atomic
    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        approval = self.get_object()

        approval_request_validation(self.request.user, "reject", approval)

        serializer = ApprovalRequestSerializer(approval, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        obj = on_reject(approval, approval.requisition, request_user=request.user)
        approval_detail = ApprovalDetailSerializer(obj, context=self.get_serializer_context()).data

        return Response(approval_detail)


@extend_schema(
    summary="List approvals owned by the current user",
    request=None,
    responses=ApprovalListSerializer,
)
class ApprovalMineListView(generics.ListAPIView):
    http_method_names = ["get"]
    permission_classes = [IsAuthenticated]
    serializer_class = ApprovalListSerializer
    pagination_class = ApprovalPagination
    ordering_fields = ["created_at", "updated_at"]

    def get_queryset(self):
        return (
            Approval.objects.active()  # type: ignore
            .filter(approver=self.request.user)
            .exclude(status=ApprovalStatusChoices.CANCELLED)
            .select_related("approver", "created_by", "updated_by")
        )
