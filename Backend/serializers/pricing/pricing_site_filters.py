from rest_framework import serializers

from Backend.serializers.common.validators import (
    CapacityRangeValidationMixin,
)
from Backend.serializers.common.choices import (
    FUNNEL_STATUSES,
    PERIOD_UNITS,
)

class PricingSiteBaseFilterSerializer(
    CapacityRangeValidationMixin,
    serializers.Serializer,
):
    period_value = serializers.IntegerField(
        required=False,
        min_value=1,
    )
    period_unit = serializers.ChoiceField(
        required=False,
        choices=PERIOD_UNITS,
    )
    client = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )
    funnel_status = serializers.ListField(
        child=serializers.ChoiceField(choices=FUNNEL_STATUSES),
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
    dane = serializers.ListField(
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
    def validate(self, attrs):
        attrs = super().validate(attrs)
        period_value = attrs.get('period_value')
        period_unit = attrs.get('period_unit')
        if (period_value is None) != (period_unit is None):
            raise serializers.ValidationError('period_value y period_unit deben especificarse juntos.')
        return attrs

class PricingSiteFilterSerializer(PricingSiteBaseFilterSerializer):
    funnel = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )
    page = serializers.IntegerField(
        required=False,
        min_value=1,
        default=1,
    )
    page_size = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=100,
        default=50,
    )

class PricingSiteFilterOptionsSerializer(PricingSiteBaseFilterSerializer):
    pass