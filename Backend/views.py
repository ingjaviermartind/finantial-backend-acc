from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend
from . import filters

from django.db import transaction

from . import models
from . import serializers
from .permissions import IsPricing
from .permissions import IsAdmin
from .permissions import IsPricingOrAdmin

from Backend.services import active_ser_service
from Backend.services.pricing_service import PricingService
from Backend.services.quote_log_service import QuoteLogService
from Backend.dtos.Project import Project

from dataclasses import asdict

from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.permissions import AllowAny

from rest_framework.viewsets import ReadOnlyModelViewSet

from Backend.dtos.PricingRecommendation import PricingRecommendation

from django.shortcuts import get_object_or_404

# class PriceViewSet(ModelViewSet):
#     queryset = models.Price.objects.all()
#     serializer_class = serializers.PriceSerializer
#     permission_classes = [IsAuthenticated]
#     def get_queryset(self):
#         return models.Price.objects.filter(created_by=self.request.user)
#     def perform_create(self, serializer):
#         serializer.save(created_by=self.request.user)
#     @action(detail=True,methods=['post'], url_path='calculate')
#     def calculate(self, request, pk=None):
#         serializer = serializers.FinancialInputSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         data = serializer.validated_data
#         price = self.get_object()
#         version = services.calculate_financials(price, request.user, data)
#         result = version.results
#         return Response({
#             'vpn': result.vpn,
#             'income_vpn': result.income_vpn,
#             'payback': result.payback,
#             'ebitda_total': result.ebitda_total,
#             'net_margin': result.net_margin,
#             'price': result.price
#         })
#     @action(detail=True, methods=['get'])
#     def versions(self, request, pk=None):
#         price = self.get_object()
#         versions = price.versions.all()
#         serializer = serializers.VersionSerializer(versions, many=True)
#         return Response(serializer.data)
    
# class VersionViewSet(ModelViewSet):
#     queryset = models.PriceVersion.objects.all()
#     serializer_class = serializers.VersionSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = [
#         "price",
#         "is_current",
#         "created_at"
#     ]
#     def get_queryset(self):
#         return models.PriceVersion.objects.filter(price__created_by=self.request.user)
#     @action(detail=True, methods=['get'])
#     def flows(self, request, pk=None):
#         version = self.get_object()
#         flows = version.flows.all()
#         serializer = serializers.CashFlowSerializer(flows, many=True)
#         return Response(serializer.data)
#     @action(detail=True, methods=['get'])
#     def results(self, request, pk=None):
#         version = self.get_object()
#         try:
#             result = version.results  # OneToOne
#         except:
#             return Response(
#                 {"error": "Results not found"},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         serializer = serializers.FinancialResultSerializer(result)
#         return Response(serializer.data)

#
# Services view sets
#
import math
from dataclasses import asdict


def replace_nan(value):
    if isinstance(value, float):
        return None if math.isnan(value) else value
    if isinstance(value, dict):
        return {
            key: replace_nan(val)
            for key, val in value.items()
        }
    if isinstance(value, list):
        return [
            replace_nan(item)
            for item in value
        ]
    return value

class DepartmentViewSet(ModelViewSet):
    authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = models.Department.objects.exclude(
        name__in=[
            'AMAZONAS',
            'ARCHIPIELAGO DE SAN ANDRES'
        ]
    ).order_by('name')
    serializer_class = serializers.DepartmentSerializer

class MunicipalityViewSet(ModelViewSet):
    authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = models.Municipality.objects.all()
    serializer_class = serializers.MunicipalitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.MunicipalityFilter

class ServicesViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    def retrieve(self, request, pk=None):
        user = request.user
        user_name = request.user.get_full_name() or request.user.username
        municipality = models.Municipality.objects.get(id=pk)
        print(f"{user_name} consultó servicios del municipio {municipality.name} del departamento {municipality.department.name}")
        result = active_ser_service.get_services_by_municipality(key=pk)
        if not result["success"]:
            status_code = (
                status.HTTP_404_NOT_FOUND
                if result["code"] == "MUNICIPALITY_NOT_FOUND"
                else status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            return Response(
                result,
                status=status_code
            )
        return Response(
            result,
            status=status.HTTP_200_OK
        )

class FinancialVariableViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]

    queryset = models.FinancialVariable.objects.all().order_by('name')
    serializer_class = serializers.FinancialVariableSerializer

    http_method_names = [
        "get",
        "patch",
        "head",
        "options"
    ]

#
# pricing view set
#
class ProductCatalogViewSet(ReadOnlyModelViewSet):
    authentication_classes = [JWTAuthentication]
    queryset = models.ProductCatalog.objects.filter(is_active=True)
    serializer_class = serializers.ProductCatalogSerializer

class SubsegmentViewSet(ReadOnlyModelViewSet):
    authentication_classes = [JWTAuthentication]
    queryset = models.Subsegment.objects.filter(is_active=True)
    serializer_class = serializers.SubsegmentSerializer


class PricingViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsPricingOrAdmin]
    @action(detail=False, methods=['post'])
    def evaluate(self, request):
        user_name = request.user.get_full_name() or request.user.username
        serializer = serializers.PricingRequestSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        municipality = models.Municipality.objects.get(
            id=data['municipality_id']
        )
        product = models.ProductCatalog.objects.get(
            id=data['product_id']
        )
        subsegment = models.Subsegment.objects.get(
            id=data['subsegment_id']
        )
        print(
            f"{user_name} evaluó "
            f"el producto {product.product} ({product.product_type}) "
            f"con una capacidad de {data['capacity_mbps']} Mbps a "
            f"{data['contract_time']} meses en el municipio "
            f"{municipality.name} del departamento "
            f"{municipality.department.name}"
        )
        prj = Project(
            capacity_mbps=data['capacity_mbps'],
            contract_time=data['contract_time'],
            initial_income=data['initial_income'],
            product_type=product.product_type,
            product=product.product,
            subsegment=subsegment.name
        )
        result : PricingRecommendation = PricingService.evaluate(
            data['municipality_id'],
            prj
        )
        QuoteLogService.create(
            result=result,
            municipality=municipality,
            product=product,
            subsegment=subsegment,
            project=prj,
            user=request.user
        )
        response_data = replace_nan(asdict(result))
        return Response(response_data)

#
# Auth
#

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = serializers.CustomTokenObtainPairSerializer

class ChangePasswordView(APIView):
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        serializer = serializers.ChangePasswordSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        user = request.user
        current_password = serializer.validated_data["current_password"]
        new_password = serializer.validated_data["new_password"]
        if not user.check_password(current_password):
            return Response(
                {
                    "detail": "La contraseña actual es incorrecta."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if user.check_password(new_password):
            return Response(
                {
                    "detail": "La nueva contraseña debe ser diferente a la actual."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response(
                {
                    "detail": e.messages
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(new_password)
        user.save()
        return Response(
            {
                "detail": "Contraseña actualizada correctamente."
            }
        )

class health(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response(
        {
            "application": "Financial Evaluator",
            "status": "UP",
            "version": "1.0.0"
        }
    )
    
#
# EOF
#