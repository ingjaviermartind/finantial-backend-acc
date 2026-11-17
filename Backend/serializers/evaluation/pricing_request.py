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
        allow_null=True,
    )

    initial_capex = serializers.FloatField(
        min_value=0,
        default=0,
    )

    def validate_price_per_mbps(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                "El precio debe ser mayor que cero."
            )
        return value

    def validate(self, attrs):
        if attrs["initial_income"] > 0 and attrs["initial_capex"] == 0:
            raise serializers.ValidationError({
                "initial_capex": (
                    "Debe indicar el CAPEX inicial cuando "
                    "se registra un ingreso inicial."
                )
            })

        return attrs