from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import exceptions, filters, generics, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .filters import USER_FILTER_FIELDS
from .models import User
from .pagination import UserPagination
from .serializers import UserDetailSerializer, UserListSerializer


class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ["get"]
    permission_classes = [IsAdminUser]
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserListSerializer
    pagination_class = UserPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = USER_FILTER_FIELDS
    ordering_fields = ["date_joined"]

    def get_object(self):
        try:
            return super().get_object()
        except Http404 as exc:
            raise exceptions.NotFound(detail="No user matches the given query.") from exc

    @extend_schema(summary="List users", request=None, responses=UserListSerializer)
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = UserListSerializer(page, many=True)

            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    @extend_schema(summary="Retrieve user", request=None, responses=UserDetailSerializer)
    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = UserDetailSerializer(user)

        return Response(serializer.data)


@extend_schema(summary="Retrieve current user", request=None, responses=UserDetailSerializer)
class UserMeRetrieveAPIView(generics.RetrieveAPIView):
    http_method_names = ["get"]
    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailSerializer

    def get_object(self):  # type: ignore
        return self.request.user
