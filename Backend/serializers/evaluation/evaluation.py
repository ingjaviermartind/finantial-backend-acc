from rest_framework import serializers

class CashFlowPeriodSerializer(serializers.Serializer):
    period = serializers.IntegerField()
    # Ingresos
    income = serializers.FloatField()

    # Desglose OPEX
    eth_output = serializers.FloatField()
    oym = serializers.FloatField()
    poles = serializers.FloatField()
    ducts = serializers.FloatField()
    call_center = serializers.FloatField()
    distribution = serializers.FloatField()
    collection = serializers.FloatField()
    opex = serializers.FloatField()

    # Cargos
    gmf = serializers.FloatField()
    fontic = serializers.FloatField()
    ica = serializers.FloatField()
    cartera = serializers.FloatField()

    # Resultados
    ebitda = serializers.FloatField()
    ebitda_ajustado = serializers.FloatField()

    # CAPEX
    web_capex = serializers.FloatField()
    initial_capex = serializers.FloatField()

    # Flujo de caja
    fcl = serializers.FloatField()
    discount_factor = serializers.FloatField()
    discounted_fcl = serializers.FloatField()
    accumulated_fcl = serializers.FloatField()
    vpn = serializers.FloatField()

class FinancialCashFlowSerializer(serializers.Serializer):
    project_snapshot = serializers.DictField()
    variables_snapshot = serializers.DictField()
    periods = CashFlowPeriodSerializer(many=True)

class PriceSummarySerializer(serializers.Serializer):
    breakeven = serializers.FloatField(allow_null=True)
    ml_price = serializers.FloatField(allow_null=True)
    tariff_base = serializers.FloatField(allow_null=True)
    tariff_discount = serializers.FloatField(allow_null=True)
    tariff_special = serializers.FloatField(allow_null=True)

class PriceDetailedSerializer(PriceSummarySerializer):
    breakeven = serializers.FloatField(allow_null=True)
    ml_price = serializers.FloatField(allow_null=True)
    suggested_price = serializers.FloatField(allow_null=True)

    sample_size = serializers.IntegerField(allow_null=True)
    source = serializers.CharField()
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
    payback = serializers.FloatField()
    payback_percent = serializers.FloatField()
    margin = serializers.FloatField()
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

