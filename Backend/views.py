from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend
from . import filters

from . import models
from . import services
from . import serializers

class PriceViewSet(ModelViewSet):
    queryset = models.Price.objects.all()
    serializer_class = serializers.PriceSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return models.Price.objects.filter(created_by=self.request.user)
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    @action(detail=True,methods=['post'], url_path='calculate')
    def calculate(self, request, pk=None):
        serializer = serializers.FinancialInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        price = self.get_object()
        version = services.calculate_financials(price, request.user, data)
        result = version.results
        return Response({
            'vpn': result.vpn,
            'income_vpn': result.income_vpn,
            'payback': result.payback,
            'ebitda_total': result.ebitda_total,
            'net_margin': result.net_margin,
            'price': result.price
        })
    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        price = self.get_object()
        versions = price.versions.all()
        serializer = serializers.VersionSerializer(versions, many=True)
        return Response(serializer.data)
    
class VersionViewSet(ModelViewSet):
    queryset = models.PriceVersion.objects.all()
    serializer_class = serializers.VersionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "price",
        "is_current",
        "created_at"
    ]
    def get_queryset(self):
        return models.PriceVersion.objects.filter(price__created_by=self.request.user)
    @action(detail=True, methods=['get'])
    def flows(self, request, pk=None):
        version = self.get_object()
        flows = version.flows.all()
        serializer = serializers.CashFlowSerializer(flows, many=True)
        return Response(serializer.data)
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        version = self.get_object()
        try:
            result = version.results  # OneToOne
        except:
            return Response(
                {"error": "Results not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = serializers.FinancialResultSerializer(result)
        return Response(serializer.data)

#
# Services view sets
#
class DepartmentViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = models.Department.objects.all()
    serializer_class = serializers.DepartmentSerializer

class MunicipalityViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = models.Municipality.objects.all()
    serializer_class = serializers.MunicipalitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.MunicipalityFilter

class ServicesViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    def retrieve(self, request, pk=None):
        try:
            data = services.get_services_by_municipality(key = pk)
            return Response(
                data,
                status= status.HTTP_200_OK
            )
        except models.Municipality.DoesNotExist:
            return Response(
                {
                    "detail": "Municipio no encontrado."
                },
                status=status.HTTP_404_NOT_FOUND
            )
#
# EOF
#