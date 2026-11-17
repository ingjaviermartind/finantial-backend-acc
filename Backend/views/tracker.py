from rest_framework import status, viewsets
from rest_framework.response import Response

from rest_framework_simplejwt.authentication import JWTAuthentication

from Backend.services.tracker import FunnelTrackerService

import math


class FunnelTrackerViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication] # JWTAuthentication
    permission_classes = [] # IsPricingOrAdmin
    def list(self, request):
        try:
            radius_m = float(request.query_params.get("radius_m", 100))
        except (TypeError, ValueError):
            return Response(
                {"detail": "radius_m debe ser un número válido."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not math.isfinite(radius_m) or radius_m <= 0:
            return Response(
                {"detail": "radius_m debe ser mayor que cero."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            result = FunnelTrackerService.get_funnel_tracker(radius_m=radius_m)
            return Response(
                result,
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {
                    "detail": (
                        "No fue posible consultar la información "
                        "de Funnel Tracker."
                    )
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )