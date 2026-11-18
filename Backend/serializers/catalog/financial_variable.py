from rest_framework import serializers
from Backend.models import FinancialVariable

class FinancialVariableSerializer(serializers.ModelSerializer):
    area_name = serializers.CharField(
        source='area.name',
        read_only=True
    )
    class Meta:
        model = FinancialVariable
        fields = [
            'id',
            'key',
            'name',
            'value',
            'unit',
            'area',
            'area_name',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'key',
            'name',
            'unit',
            'area',
            'area_name',
            'updated_at',
        ]

    def validate_value(self, value):
        key = getattr(self.instance, 'key', None)
        if value < 0:
            raise serializers.ValidationError("El valor no puede ser negativo.")
        
        if key in {'TRM', 'WACC'} and value <= 0:
            raise serializers.ValidationError("Esta variable debe ser mayor que cero.")

        return value