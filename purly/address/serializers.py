from rest_framework import serializers

from purly.user.serializers import UserDetailSerializer
from purly.utils import CustomToRepresentation

from .models import Address


class AddressListSerializer(CustomToRepresentation, serializers.ModelSerializer):
    owner = UserDetailSerializer(read_only=True)
    created_by = UserDetailSerializer(read_only=True)
    updated_by = UserDetailSerializer(read_only=True)

    class Meta:
        model = Address
        fields = [
            "id",
            "name",
            "address_code",
            "description",
            "attention",
            "phone",
            "street1",
            "street2",
            "city",
            "state",
            "zip_code",
            "country",
            "owner",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]


class AddressDetailSerializer(CustomToRepresentation, serializers.ModelSerializer):
    owner = UserDetailSerializer(read_only=True)
    created_by = UserDetailSerializer(read_only=True)
    updated_by = UserDetailSerializer(read_only=True)

    class Meta:
        model = Address
        fields = [
            "id",
            "name",
            "address_code",
            "description",
            "attention",
            "phone",
            "street1",
            "street2",
            "city",
            "state",
            "zip_code",
            "country",
            "owner",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]


class AddressCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "name",
            "address_code",
            "description",
            "attention",
            "phone",
            "street1",
            "street2",
            "city",
            "state",
            "zip_code",
            "country",
            "owner",
        ]
        extra_kwargs = {
            "owner": {
                "error_messages": {
                    "does_not_exist": "This user does not exist: {pk_value}",
                }
            },
        }


class AddressUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "name",
            "address_code",
            "description",
            "attention",
            "phone",
            "street1",
            "street2",
            "city",
            "state",
            "zip_code",
            "country",
            "owner",
        ]
