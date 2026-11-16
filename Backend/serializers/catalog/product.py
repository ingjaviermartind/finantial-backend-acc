from rest_framework import serializers
from Backend.models import ProductCatalog

class ProductCatalogSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()
    product_type = serializers.CharField()
    product = serializers.CharField()

    class Meta:
        model = ProductCatalog
        fields = [
            'id',
            'product_type',
            'product'
        ]