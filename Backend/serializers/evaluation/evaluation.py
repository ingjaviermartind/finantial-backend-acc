from rest_framework import serializers

class PriceComparisonSerializer(serializers.Serializer):
    breakeven = serializers.FloatField(allow_null=True)
    ml_price = serializers.FloatField(allow_null=True)
    suggested_price = serializers.FloatField(allow_null=True)
    evaluated_price = serializers.FloatField(allow_null=True)

    market_average = serializers.FloatField(allow_null=True)
    market_median = serializers.FloatField(allow_null=True)

    tariff_base = serializers.FloatField(allow_null=True)
    tariff_discount = serializers.FloatField(allow_null=True)
    tariff_special = serializers.FloatField(allow_null=True)

class EvaluationSummarySerializer(serializers.Serializer):
    approved = serializers.BooleanField()
    price_monthly = serializers.FloatField()
    price_per_mbps = serializers.FloatField()


class EvaluationDetailedSerializer(EvaluationSummarySerializer):
    capex = serializers.FloatField()
    opex_m = serializers.FloatField()
    vpn = serializers.FloatField()
    tir = serializers.FloatField()
    payback = serializers.IntegerField(allow_null=True)
    payback_percent = serializers.FloatField()
    margin = serializers.FloatField()
    cashflows = serializers.ListField(
        child=serializers.FloatField()
    )

class PricingRecommendationSummarySerializer(serializers.Serializer):
    suggested = EvaluationSummarySerializer()
    predicted = EvaluationSummarySerializer()
    floor = EvaluationSummarySerializer()


class PricingRecommendationDetailedSerializer(
    PricingRecommendationSummarySerializer
):
    suggested = EvaluationDetailedSerializer()
    predicted = EvaluationDetailedSerializer()
    floor = EvaluationDetailedSerializer()

    price_comparison = PriceComparisonSerializer()
    # mean_price_mbps = serializers.FloatField()
    # median_price_mbps = serializers.FloatField()
    # market_std = serializers.FloatField()
    # market_source = serializers.CharField()
    # monthly_wacc = serializers.FloatField()
    # wacc = serializers.FloatField()
    # market_sample = serializers.IntegerField()
    # ref_price_mbps = serializers.FloatField()
    # ref_price_mbps_dis = serializers.FloatField()
    # ref_price_mbps_special = serializers.FloatField()