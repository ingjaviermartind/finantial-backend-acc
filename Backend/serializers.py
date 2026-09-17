from rest_framework import serializers
from . import models

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password

from django.contrib.auth.models import update_last_login

# class PriceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.Price
#         fields = '__all__'

# class VersionSerializer(serializers.ModelSerializer):
#     created_by = serializers.StringRelatedField(read_only=True)
#     class Meta:
#         model = models.PriceVersion
#         fields = [
#             "id",
#             "price",
#             "horizon",
#             "payment_type",
#             "version_number",
#             "is_current",
#             "created_at",
#             "updated_at",
#             "created_by",
#         ]
#         read_only_fields = [
#             "id",
#             "version_number",
#             "is_current",
#             "created_at",
#             "updated_at",
#             "created_by",
#         ]

# class CashFlowSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.CashFlow
#         fields = '__all__'

# class FinancialResultsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.FinancialResults
#         fields = '__all__'

# class FinancialInputSerializer(serializers.Serializer):
    # horizon = serializers.IntegerField()
    # inicial_income = serializers.FloatField(default=0.0)
    # capex = serializers.FloatField()
    # opex = serializers.FloatField()
    # wacc = serializers.FloatField()
    # factor = serializers.FloatField(required=False, default=1.0)
    # sensitivity = serializers.FloatField(required=False, default=1.0)
    # payment_type = serializers.ChoiceField(choices=['one time', 'monthly'])
    # payment_duration = serializers.FloatField()
    # class meta:
    #     model = models.FinancialInputs
    #     fields = [
    #         'id',
    #         # 'horizon',
    #         'inicial_income',
    #         'capex',
    #         'opex',
    #         'wacc',
    #         'factor',
    #         'sensitivity',
    #         # 'payment_type',
    #         # 'payment_duration'
    #     ]

# class FinancialResultSerializer(serializers.Serializer):
#     vpn = serializers.FloatField()
#     income_vpn = serializers.FloatField()
#     payback = serializers.IntegerField()
#     contribution_percent = serializers.FloatField()
#     ebitda_total = serializers.FloatField()
#     net_margin = serializers.FloatField()
#     price = serializers.FloatField()
#     class meta:
#         model = models.FinancialResults
#         fields = [
#             'id',
#             'vpn',
#             'income_vpn',
#             'payback',
#             'contribution',
#             'ebitda_total',
#             'net_margin',
#             'price'
#         ]

#
# Services Serializers 
#

class DepartmentSerializer(serializers.Serializer):
    name = serializers.CharField()
    id = serializers.UUIDField()
    class Meta:
        model = models.Department
        fields = [
            'id',
            'name'
        ]

class MunicipalitySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    dane = serializers.IntegerField()
    region = serializers.CharField(
        source='region.name',
        allow_null=True
    )
    node = serializers.CharField(allow_null=True)
    class Meta:
        model = models.Municipality
        fields = [
            'id',
            'name',
            'dane',
            'region',
            'node'
        ]

class PricingRequestSerializer(serializers.Serializer):
    municipality_id = serializers.UUIDField()
    product_id = serializers.CharField()
    subsegment_id = serializers.CharField()
    capacity_mbps = serializers.FloatField(min_value=1)
    contract_time = serializers.IntegerField(min_value=1)
    initial_income = serializers.FloatField(default=0)

class FinancialVariableSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.FinancialVariable
        fields = [
            'id',
            'key',
            'name',
            'value',
            'unit',
            'updated_at'
        ]

        read_only_fields = [
            "id",
            "key",
            "name",
            "unit",
            "updated_at"
        ]

    def validate_value(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "El valor no puede ser negativo."
            )
        if self.instance.key in [
            "TRM",
            "WACC",
        ] and value <= 0:
            raise serializers.ValidationError(
                "Esta variable debe ser mayor que cero."
            )
        return value

class ProductCatalogSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()
    product_type = serializers.CharField()
    product = serializers.CharField()

    class Meta:
        model = models.ProductCatalog
        fields = [
            'id',
            'product_type',
            'product'
        ]

class SubsegmentSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    class Meta:
        model = models.Subsegment
        fields = [
            'id',
            'name'
        ]

#
# auth Serializers 
#


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        profile = getattr(user, "profile", None)
        update_last_login(None, self.user)
        data["user"] = {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "groups": list(
                user.groups.values_list("name", flat=True)
            ),
            "area": profile.area if profile else None,
            "cargo": profile.cargo if profile else None,
        }
        return data

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        write_only=True
    )
    new_password = serializers.CharField(
        write_only=True,
        min_length=8
    )
    def validate_new_password(self, value):
        validate_password(value)
        return value

class PricingSiteFilterSerializer(serializers.Serializer):
    FUNNEL_STATUSES = [
        "Cliente Acepta",
        "Cliente no acepta",
        "Devuelto mesa de control",
        "Devuelto por Preventa",
        "En validación comercial",
        "En validación preventa",
        "En validación pricing",
        "Gestionado mesa de control",
        "Negociación cliente",
    ]

    period_value = serializers.IntegerField(
        required=False,
        min_value=1
    )
    period_unit = serializers.ChoiceField(
        required=False,
        choices=[
            'día(s)',
            'semana(s)',
            'mes(es)',
            'trimestre(s)',
            'año(s)'
        ]
    )
    client = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    funnel_status = serializers.ListField(
        child=serializers.ChoiceField(
            choices=FUNNEL_STATUSES
        ),
        required=False
    )
    capacity_min = serializers.FloatField(
        required=False,
        min_value=0
    )
    capacity_max = serializers.FloatField(
        required=False,
        min_value=0
    )
    department = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    municipality = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    dane = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    product = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    plan = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    product_family = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    page = serializers.IntegerField(
        required=False,
        min_value=1,
        default=1
    )
    page_size = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=100,
        default=50
    )
    def validate(self, attrs):
        period_value = attrs.get("period_value")
        period_unit = attrs.get("period_unit")
        if period_value is not None and period_unit is None:
            raise serializers.ValidationError(
                "period_unit es requerido cuando se especifica period_value."
            )
        if period_unit is not None and period_value is None:
            raise serializers.ValidationError(
                "period_value es requerido cuando se especifica period_unit."
            )
        capacity_min = attrs.get("capacity_min")
        capacity_max = attrs.get("capacity_max")
        if (
            capacity_min is not None
            and capacity_max is not None
            and capacity_min > capacity_max
        ):
            raise serializers.ValidationError(
                "capacity_min no puede ser mayor que capacity_max."
            )
        return attrs

class PricingSiteFilterOptionsSerializer(serializers.Serializer):

    FUNNEL_STATUSES = [
            "Cliente Acepta",
            "Cliente no acepta",
            "Devuelto mesa de control",
            "Devuelto por Preventa",
            "En validación comercial",
            "En validación preventa",
            "En validación pricing",
            "Gestionado mesa de control",
            "Negociación cliente",
        ]

    period_value = serializers.IntegerField(
        required=False,
        min_value=1
    )

    period_unit = serializers.ChoiceField(
        required=False,
        choices=[
            "día(s)",
            "semana(s)",
            "mes(es)",
            "trimestre(s)",
            "año(s)",
        ]
    )

    client = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )

    funnel_status = serializers.ListField(
        child=serializers.ChoiceField(
            choices=FUNNEL_STATUSES
        ),
        required=False
    )

    capacity_min = serializers.FloatField(
        required=False,
        min_value=0
    )

    capacity_max = serializers.FloatField(
        required=False,
        min_value=0
    )

    department = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )

    municipality = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )

    dane = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )

    product = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )

    plan = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )

    product_family = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )

    def validate(self, attrs):
        period_value = attrs.get("period_value")
        period_unit = attrs.get("period_unit")

        if period_value is not None and period_unit is None:
            raise serializers.ValidationError(
                "period_unit es requerido cuando se especifica period_value."
            )

        if period_unit is not None and period_value is None:
            raise serializers.ValidationError(
                "period_value es requerido cuando se especifica period_unit."
            )

        capacity_min = attrs.get("capacity_min")
        capacity_max = attrs.get("capacity_max")

        if (
            capacity_min is not None
            and capacity_max is not None
            and capacity_min > capacity_max
        ):
            raise serializers.ValidationError(
                "capacity_min no puede ser mayor que capacity_max."
            )

        return attrs
#
# EOF
#