from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework_simplejwt.authentication import JWTAuthentication

from django.http import HttpResponse

from Backend.filters import PricingSiteFilterOptions, PricingSiteFilters
from Backend.serializers import PricingSiteFilterOptionsSerializer, PricingSiteFilterSerializer
from Backend.services.pricing_site_service import PricingSiteService


class PricingSiteViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = []
    def list(self, request):
        filters = self._get_filters(request)
        result = PricingSiteService.get_priced_sites(filters)
        return Response(result)

    @action(
        detail=False,
        methods=["get"],
        url_path="filter-options"
    )
    def filter_options(self, request):
        serializer = PricingSiteFilterOptionsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        filter_option = PricingSiteFilterOptions(
            period_value=data.get("period_value"),
            period_unit=data.get("period_unit"),
            clients=data.get("client", []),
            funnel_statuses=data.get("funnel_status", []),
            capacity_min=data.get("capacity_min"),
            capacity_max=data.get("capacity_max"),
            departments=data.get("department", []),
            municipalities=data.get("municipality", []),
            danes=data.get("dane", []),
            products=data.get("product", []),
            plans=data.get("plan", []),
            product_families=data.get("product_family", []),
        )
        result = PricingSiteService.get_filter_options(filter_option)
        return Response(result)
    @action(
        detail=False,
        methods=["get"],
        url_path="export"
    )
    def export(self, request):
        filters = self._get_filters(request)
        excel_file = PricingSiteService.export_priced_sites(filters)
        response = HttpResponse(
            excel_file,
            content_type=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        )
        response["Content-Disposition"] = (
            'attachment; filename="pricing_sites.xlsx"'
        )
        return response
    @action(
        detail=True,
        methods=["get"],
        url_path="pricings"
    )
    def pricings(self, request, pk=None):
        # result = self.service.get_site_pricings(pk)
        result = {
            "application": "Financial Evaluator",
            "status": "UP",
            "version": "1.0.0"
        }
        return Response(result)
    def _get_filters(self, request):
        serializer = PricingSiteFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return PricingSiteFilters(
            period_value=data.get('period_value'),
            period_unit=data.get('period_unit'),
            clients=data.get('client', []),
            funnels=data.get('funnel', []),
            funnel_statuses=data.get('funnel_status', []),
            capacity_min=data.get('capacity_min'),
            capacity_max=data.get('capacity_max'),
            departments=data.get('department', []),
            municipalities=data.get('municipality', []),
            danes=data.get('dane', []),
            products=data.get('product', []),
            plans=data.get('plan', []),
            product_families=data.get('product_family', []),
            page=data.get('page', 1),
            page_size=data.get('page_size', 50),
        )