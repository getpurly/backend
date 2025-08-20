from rest_framework import serializers

from purly.user.serializers import UserSimpleDetailSerializer
from purly.utils import CustomToRepresentation

from .models import Address


class AddressListSerializer(CustomToRepresentation, serializers.ModelSerializer):
    owner = UserSimpleDetailSerializer(read_only=True)
    created_by = UserSimpleDetailSerializer(read_only=True)
    updated_by = UserSimpleDetailSerializer(read_only=True)

    class Meta:
        model = Address
        fields = [
            "id",
            "owner",
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
            "delivery_instructions",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]


class AddressDetailSerializer(CustomToRepresentation, serializers.ModelSerializer):
    owner = UserSimpleDetailSerializer(read_only=True)
    created_by = UserSimpleDetailSerializer(read_only=True)
    updated_by = UserSimpleDetailSerializer(read_only=True)

    class Meta:
        model = Address
        fields = [
            "id",
            "owner",
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
            "delivery_instructions",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]


class AddressSimpleDetailSerializer(CustomToRepresentation, serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "name",
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
            "delivery_instructions",
        ]


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
            "delivery_instructions",
        ]
