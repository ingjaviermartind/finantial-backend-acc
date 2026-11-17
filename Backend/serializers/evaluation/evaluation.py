from rest_framework import serializers


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

    mean_price_mbps = serializers.FloatField()
    median_price_mbps = serializers.FloatField()
    market_std = serializers.FloatField()
    market_source = serializers.CharField()
    monthly_wacc = serializers.FloatField()
    wacc = serializers.FloatField()
    market_sample = serializers.IntegerField()
    ref_price_mbps = serializers.FloatField()
    ref_price_mbps_dis = serializers.FloatField()
    ref_price_mbps_special = serializers.FloatField()