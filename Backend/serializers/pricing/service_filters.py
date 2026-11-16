from rest_framework import serializers

from Backend.serializers.common.validators import (
    CapacityRangeValidationMixin,
)


class ServiceFilterSerializer(
    CapacityRangeValidationMixin,
    serializers.Serializer,
):
    subsegment = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )
    client = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )
    capacity_min = serializers.FloatField(
        required=False,
        min_value=0,
    )
    capacity_max = serializers.FloatField(
        required=False,
        min_value=0,
    )
    department = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )
    municipality = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )
    product = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )
    plan = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )
    product_family = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )