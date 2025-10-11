from rest_framework import serializers

from purly.base import CustomToRepresentation

from .models import CustomUser


class UserDetailSerializer(CustomToRepresentation, serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "first_name", "last_name", "email", "is_active", "date_joined"]


class UserSimpleDetailSerializer(CustomToRepresentation, serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username"]


class UserListSerializer(CustomToRepresentation, serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "first_name", "last_name", "email", "is_active", "date_joined"]
