from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, filters, generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import ADDRESS_FILTER_FIELDS
from .models import Address
from .pagination import AddressPagination
from .serializers import (
    AddressCreateSerializer,
    AddressDetailSerializer,
    AddressListSerializer,
    AddressUpdateSerializer,
)


class AddressViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "put"]
    permission_classes = [IsAuthenticated]
    queryset = Address.objects.select_related("owner", "created_by", "updated_by").all()
    serializer_class = AddressListSerializer
    pagination_class = AddressPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ADDRESS_FILTER_FIELDS
    ordering_fields = ["created_at", "updated_at"]

    def get_object(self):
        try:
            return super().get_object()
        except Http404 as exc:
            raise exceptions.NotFound(detail="No address matches the given query.") from exc

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = AddressListSerializer(page, many=True)

            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(self.get_queryset(), many=True)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = AddressCreateSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        obj = serializer.save(
            owner=self.request.user, created_by=self.request.user, updated_by=self.request.user
        )
        address_detail = AddressDetailSerializer(obj, context=self.get_serializer_context()).data

        return Response(address_detail, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        address = self.get_object()
        serializer = AddressDetailSerializer(address)

        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        address = self.get_object()
        serializer = AddressUpdateSerializer(address, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        obj = serializer.save(updated_by=self.request.user)
        address_detail = AddressDetailSerializer(obj, context=self.get_serializer_context()).data

        return Response(address_detail, status=status.HTTP_200_OK)


class AddressMineListView(generics.ListAPIView):
    http_method_names = ["get"]
    permission_classes = [IsAuthenticated]
    serializer_class = AddressListSerializer
    pagination_class = AddressPagination
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ADDRESS_FILTER_FIELDS
    ordering_fields = ["created_at", "updated_at"]

    def get_queryset(self): # type: ignore
        return Address.objects.select_related("owner", "created_by", "updated_by").filter(
            owner=self.request.user
        )
