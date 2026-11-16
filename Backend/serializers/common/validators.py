from rest_framework import serializers

class CapacityRangeValidationMixin:
    def validate(self, attrs):
        attrs = super().validate(attrs)
        capacity_min = attrs.get('capacity_min')
        capacity_max = attrs.get('capacity_max')
        if (
            capacity_min is not None
            and capacity_max is not None
            and capacity_min > capacity_max
        ):
            raise serializers.ValidationError({
                'capacity_max': (
                    'capacity_max no puede ser menor que capacity_min.'
                )
            })
        return attrs