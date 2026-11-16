from rest_framework import serializers
from Backend.models import Subsegment

class SubsegmentSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    class Meta:
        model = Subsegment
        fields = [
            'id',
            'name'
        ]
