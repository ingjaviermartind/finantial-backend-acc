from rest_framework import serializers
from Backend.models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    unprofitable = serializers.BooleanField(read_only=True)
    class Meta:
        model = Department
        fields = [
            'id',
            'name',
            'unprofitable',
        ]
        read_only_fields = fields