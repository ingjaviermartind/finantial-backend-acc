from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from rest_framework_simplejwt.authentication import JWTAuthentication

from Backend.models import FinancialVariable
from Backend.permissions import IsAdmin
from rest_framework.response import Response
from Backend.serializers import FinancialVariableSerializer

class FinancialVariableViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]
    serializer_class = FinancialVariableSerializer
    http_method_names = ["get", "patch", "head", "options"]
    def get_queryset(self):
        queryset = FinancialVariable.objects.select_related(
            "area"
        ).order_by("name")
        area = self.request.query_params.get("area")
        if area:
            queryset = queryset.filter(area__key=area)
        return queryset

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