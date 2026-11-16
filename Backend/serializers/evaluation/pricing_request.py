from rest_framework import serializers


class PricingRequestSerializer(serializers.Serializer):
    municipality_id = serializers.UUIDField()
    product_id = serializers.UUIDField()
    subsegment_id = serializers.UUIDField()

    capacity_mbps = serializers.FloatField(min_value=1)
    contract_time = serializers.IntegerField(min_value=1)

    initial_income = serializers.FloatField(
        min_value=0,
        default=0,
    )

    price_per_mbps = serializers.FloatField(
        min_value=0,
        required=False,
    )

    initial_capex = serializers.FloatField(
        min_value=0,
        default=0,
    )