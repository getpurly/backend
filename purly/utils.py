from rest_framework import serializers


class CustomToRepresentation(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)

        for key, value in data.items():
            try:
                if not value:
                    data[key] = None
            except KeyError:
                pass

        return data
