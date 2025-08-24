from django.contrib.auth import get_user_model
from rest_framework import serializers

from purly.base import CustomToRepresentation

User = get_user_model()


class UserDetailSerializer(CustomToRepresentation, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "is_active", "date_joined"]


class UserSimpleDetailSerializer(CustomToRepresentation, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class UserListSerializer(CustomToRepresentation, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "is_active", "date_joined"]
