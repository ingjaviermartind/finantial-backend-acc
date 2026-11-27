from rest_framework import serializers

class CashFlowPeriodSerializer(serializers.Serializer):
    period = serializers.IntegerField()
    income = serializers.DecimalField(
        max_digits=24,
        decimal_places=6
    )

    capex_breakdown = serializers.DictField(
        child=serializers.DecimalField(
            max_digits=24,
            decimal_places=6
        )
    )

    opex_breakdown = serializers.DictField(
        child=serializers.DecimalField(
            max_digits=24,
            decimal_places=6
        )
    )

    capex = serializers.DecimalField(max_digits=24, decimal_places=6)
    opex = serializers.DecimalField(max_digits=24, decimal_places=6)

    gmf = serializers.DecimalField(max_digits=24, decimal_places=6)
    fontic = serializers.DecimalField(max_digits=24, decimal_places=6)
    ica = serializers.DecimalField(max_digits=24, decimal_places=6)
    cartera = serializers.DecimalField(max_digits=24, decimal_places=6)

    ebitda = serializers.DecimalField(max_digits=24, decimal_places=6)
    ebitda_ajustado = serializers.DecimalField(max_digits=24, decimal_places=6)

    fcl = serializers.DecimalField(max_digits=24, decimal_places=6)

    discount_factor = serializers.DecimalField(
        max_digits=24,
        decimal_places=12
    )

    discounted_fcl = serializers.DecimalField(
        max_digits=24,
        decimal_places=6
    )

    accumulated_fcl = serializers.DecimalField(
        max_digits=24,
        decimal_places=6
    )

    vpn = serializers.DecimalField(max_digits=24, decimal_places=6)
    income_vpn = serializers.DecimalField(max_digits=24, decimal_places=6)

class FinancialCashFlowSerializer(serializers.Serializer):
    project_snapshot = serializers.DictField()
    variables_snapshot = serializers.DictField()
    periods = CashFlowPeriodSerializer(many=True)

class PriceSummarySerializer(serializers.Serializer):
    breakeven = serializers.DecimalField(
        max_digits=24,
        decimal_places=6,
        allow_null=True
    )
    ml_price = serializers.DecimalField(
        max_digits=24,
        decimal_places=6,
        allow_null=True
    )
    tariff_base = serializers.DecimalField(
        max_digits=24,
        decimal_places=6,
        allow_null=True
    )
    tariff_discount = serializers.DecimalField(
        max_digits=24,
        decimal_places=6,
        allow_null=True
    )
    tariff_special = serializers.DecimalField(
        max_digits=24,
        decimal_places=6,
        allow_null=True
    )


class PriceDetailedSerializer(PriceSummarySerializer):
    sample_size = serializers.IntegerField(allow_null=True)
    source = serializers.CharField(allow_null=True)
    market_average = serializers.DecimalField(
        max_digits=24,
        decimal_places=6,
        allow_null=True
    )
    market_median = serializers.DecimalField(
        max_digits=24,
        decimal_places=6,
        allow_null=True
    )

class EvaluationSummarySerializer(serializers.Serializer):
    approved = serializers.BooleanField()
    price_monthly = serializers.DecimalField(max_digits=24, decimal_places=6)
    price_per_mbps = serializers.DecimalField(max_digits=24, decimal_places=6)


class EvaluationDetailedSerializer(EvaluationSummarySerializer):
    capex = serializers.DecimalField(max_digits=24, decimal_places=6)
    opex_m = serializers.DecimalField(max_digits=24, decimal_places=6)
    vpn = serializers.DecimalField(max_digits=24, decimal_places=6)
    tir = serializers.DecimalField(
        max_digits=24,
        decimal_places=12,
        allow_null=True
    )
    payback = serializers.DecimalField(
        max_digits=24,
        decimal_places=8,
        allow_null=True
    )
    payback_percent = serializers.DecimalField(
        max_digits=24,
        decimal_places=12
    )
    margin = serializers.DecimalField(
        max_digits=24,
        decimal_places=12
    )
    financial_cashflow = FinancialCashFlowSerializer()

class PricingRecommendationSummarySerializer(serializers.Serializer):
    suggested = EvaluationSummarySerializer()
    predicted = EvaluationSummarySerializer()
    floor = EvaluationSummarySerializer()
    price_comparison = PriceSummarySerializer()

class PricingRecommendationDetailedSerializer(PricingRecommendationSummarySerializer):
    suggested = EvaluationDetailedSerializer()
    predicted = EvaluationDetailedSerializer()
    floor = EvaluationDetailedSerializer()
    price_comparison = PriceDetailedSerializer()

