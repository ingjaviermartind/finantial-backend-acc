from rest_framework import serializers
from Backend.models import Municipality

class MunicipalitySerializer(serializers.ModelSerializer):
    region = serializers.CharField(
        source='region.name',
        read_only=True,
        allow_null=True,
    )
    class Meta:
        model = Municipality
        fields = [
            'id',
            'name',
            'dane',
            'region',
            'node',
            'unprofitable',
        ]
        read_only_fields = fields