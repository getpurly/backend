from django.contrib.auth import get_user_model
from rest_framework import serializers

from purly.utils import CustomToRepresentation

User = get_user_model()


class UserDetailSerializer(CustomToRepresentation, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "is_active", "date_joined"]


class UserListSerializer(CustomToRepresentation, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "is_active", "date_joined"]
