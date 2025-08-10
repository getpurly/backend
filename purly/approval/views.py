from django.db import transaction
from django.http import Http404
from rest_framework import exceptions, generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.exceptions import BadRequest

from .models import Approval, ApprovalStatusChoices
from .pagination import ApprovalPagination
from .serializers import (
    ApprovalApproveSerializer,
    ApprovalDetailSerializer,
    ApprovalListSerializer,
    ApprovalRejectSerializer,
)
from .services import check_current_approver


class ApprovalViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post"]
    permission_classes = [IsAuthenticated]
    queryset = Approval.objects_active.select_related("approver", "created_by", "updated_by").all()
    serializer_class = ApprovalListSerializer
    pagination_class = ApprovalPagination

    def get_object(self):
        try:
            return super().get_object()
        except Http404 as exc:
            raise exceptions.NotFound(detail="No approval matches the given query.") from exc

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = ApprovalListSerializer(page, many=True)

            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(self.get_queryset(), many=True)

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        approval = self.get_object()
        serializer = ApprovalDetailSerializer(approval)

        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        approval = self.get_object()

        if approval.approver != self.request.user:
            raise exceptions.PermissionDenied("You cannot approve on someone else's behalf.")

        if approval.status != ApprovalStatusChoices.PENDING:
            raise BadRequest(detail="This approval must be in pending status to approve.")

        if check_current_approver(approval) is False:
            raise BadRequest(detail="An earlier approval is still pending.")

        serializer = ApprovalApproveSerializer(approval, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        obj = serializer.save(updated_by=self.request.user)
        approval_detail = ApprovalDetailSerializer(obj, context=self.get_serializer_context()).data

        return Response(approval_detail)

    @transaction.atomic
    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        approval = self.get_object()

        if approval.approver != self.request.user:
            raise exceptions.PermissionDenied("You cannot reject on someone else's behalf.")

        if approval.status != ApprovalStatusChoices.PENDING:
            raise BadRequest(detail="This approval must be in pending status to reject.")

        if check_current_approver(approval) is False:
            raise BadRequest(detail="An earlier approval is still pending.")

        serializer = ApprovalRejectSerializer(approval, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        obj = serializer.save(updated_by=self.request.user)
        approval_detail = ApprovalDetailSerializer(obj, context=self.get_serializer_context()).data

        return Response(approval_detail)


class ApprovalMineListView(generics.ListAPIView):
    http_method_names = ["get"]
    permission_classes = [IsAuthenticated]
    serializer_class = ApprovalListSerializer
    pagination_class = ApprovalPagination

    def get_queryset(self):  # type: ignore
        return Approval.objects_active.filter(approver=self.request.user).exclude(
            status=ApprovalStatusChoices.CANCELLED
        )
