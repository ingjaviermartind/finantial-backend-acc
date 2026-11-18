from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework_simplejwt.authentication import JWTAuthentication

from Backend.dtos import Project, PricingRecommendation
from Backend.permissions import CanEvaluate, can_view_detailed_results
from Backend.models import Municipality, ProductCatalog, Subsegment
from Backend.serializers import (PricingRequestSerializer, 
                                 PricingRecommendationDetailedSerializer, 
                                 PricingRecommendationSummarySerializer, 
                                 EvaluationSummarySerializer, 
                                 EvaluationDetailedSerializer)
from Backend.services.pricing_service import PricingService
from Backend.services.quote_log_service import QuoteLogService

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

import logging
import math
from dataclasses import asdict

logger = logging.getLogger(__name__)

def replace_nan(value):
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {
            key: replace_nan(val)
            for key, val in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [
            replace_nan(item)
            for item in value
        ]
    return value



class PricingViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [CanEvaluate]
    @action(detail=False, methods=['post'])
    def evaluate(self, request):
        # user_name = request.user.get_full_name() or request.user.username
        serializer = PricingRequestSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        municipality = get_object_or_404(
            Municipality,
            id=data["municipality_id"]
        )
        product = get_object_or_404(
            ProductCatalog,
            id=data["product_id"]
        )
        subsegment = get_object_or_404(
            Subsegment,
            id=data["subsegment_id"]
        )
        logger.info(
            "Evaluación de producto %s (%s), capacidad %s Mbps, "
            "contrato %s meses, municipio %s, departamento %s.",
            product.product,
            product.product_type,
            data["capacity_mbps"],
            data["contract_time"],
            municipality.name,
            municipality.department.name,
            extra={
                "username": request.user.username,
                "user_id": request.user.id,
            }
        )
        prj = Project(
            capacity_mbps=data['capacity_mbps'],
            contract_time=data['contract_time'],
            initial_income=data['initial_income'],
            initial_capex=data['initial_capex'],
            product_type=product.product_type,
            product=product.product,
            subsegment=subsegment.name
        )
        area = request.user.profile.area
        result : PricingRecommendation = PricingService.evaluate(
            data['municipality_id'],
            prj,
            area
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
        serializer_class = self.get_recommendation_serializer()
        serializer = serializer_class(
            response_data,
            context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def evaluate_price(self, request):
        user_name = (
            request.user.get_full_name()
            or request.user.username
        )
        serializer = PricingRequestSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        price_per_mbps = data.get("price_per_mbps")
        if price_per_mbps is None or price_per_mbps <= 0:
            raise ValidationError({
                "price_per_mbps": "Debe ser un precio mayor que cero."
            })
        
        municipality = get_object_or_404(
            Municipality,
            id=data["municipality_id"]
        )
        product = get_object_or_404(
            ProductCatalog,
            id=data["product_id"]
        )
        subsegment = get_object_or_404(
            Subsegment,
            id=data["subsegment_id"]
        )
        logger.info(
            "Evaluó un precio de %s COP/Mbps para el producto %s (%s), "
            "con una capacidad de %s Mbps a %s meses, en el municipio "
            "%s del departamento %s.",
            price_per_mbps,
            product.product,
            product.product_type,
            data["capacity_mbps"],
            data["contract_time"],
            municipality.name,
            municipality.department.name,
            extra={
                "username": request.user.username,
                "user_id": request.user.id,
            }
        )
        prj = Project(
            capacity_mbps=data['capacity_mbps'],
            contract_time=data['contract_time'],
            initial_income=data['initial_income'],
            initial_capex=data['initial_capex'],
            product_type=product.product_type,
            product=product.product,
            subsegment=subsegment.name
        )
        area = request.user.profile.area
        result = PricingService.evaluate_price(prj, price_per_mbps, area)
        response_data = replace_nan(asdict(result))
        serializer_class = self.get_evaluation_serializer()
        serializer = serializer_class(
            response_data,
            context={"request": request}
        )
        return Response(serializer.data)

    def get_recommendation_serializer(self):
        if can_view_detailed_results(self.request.user):
            return PricingRecommendationDetailedSerializer
        return PricingRecommendationSummarySerializer


    def get_evaluation_serializer(self):
        if can_view_detailed_results(self.request.user):
            return EvaluationDetailedSerializer
        return EvaluationSummarySerializer