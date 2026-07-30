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
from Backend.services import services
from . import serializers
from .permissions import IsPricing
from .permissions import IsAdmin
from .permissions import IsPricingOrAdmin

from Backend.services import active_ser_service
from Backend.services.pricing_service import PricingService
from Backend.dtos.Project import Project

from dataclasses import asdict

from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.permissions import AllowAny

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
    authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = models.Department.objects.all()
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
        try:
            data = active_ser_service.get_services_by_municipality(key = pk)
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

class PricingViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsPricingOrAdmin]
    @action(detail=False, methods=['post'])
    def evaluate(self, request):
        serializer = serializers.PricingRequestSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        prj = Project(
            capacity_mbps=data['capacity_mbps'],
            contract_time=data['contract_time'],
            initial_income=data['initial_income']
        )
        result = PricingService.evaluate(data['municipality_id'], prj)
        return Response(asdict(result))

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