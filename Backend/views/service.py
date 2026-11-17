from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework_simplejwt.authentication import JWTAuthentication

from Backend.services import active_ser_service
from Backend.serializers import ServiceFilterSerializer

from Backend.filters import ServiceFilters

import logging
logger = logging.getLogger(__name__)


class ServicesViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]

    def list(self, request):
        service_filters = self._get_filters(request)
        try:
            result = active_ser_service.get_services(service_filters)
            return Response(
                result,
                status=status.HTTP_200_OK
            )
        except Exception:
            logger.exception(
                "Error al consultar servicios activos.",
                extra={
                    "username": request.user.username,
                    "user_id": request.user.id,
                }
            )
            return Response(
                {"detail": "No fue posible consultar los servicios."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None):
        try:
            result = active_ser_service.get_services_by_municipality(
                key=pk
            )
            if not result["success"]:
                if result["code"] == "MUNICIPALITY_NOT_FOUND":
                    logger.warning(
                        "Se intentó consultar servicios de un municipio inexistente: %s.",
                        pk,
                        extra={
                            "username": request.user.username,
                            "user_id": request.user.id,
                        }
                    )
                    return Response(
                        {"detail": "El municipio solicitado no existe."},
                        status=status.HTTP_404_NOT_FOUND
                    )
                logger.error(
                    "El servicio de consulta por municipio devolvió un error: %s.",
                    result.get("code", "UNKNOWN"),
                    extra={
                        "username": request.user.username,
                        "user_id": request.user.id,
                    }
                )
                return Response(
                    {"detail": "No fue posible consultar los servicios del municipio."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            return Response(
                result,
                status=status.HTTP_200_OK
            )
        except Exception:
            logger.exception(
                "Error inesperado al consultar servicios del municipio %s.",
                pk,
                extra={
                    "username": request.user.username,
                    "user_id": request.user.id,
                }
            )
            return Response(
                {"detail": "No fue posible consultar los servicios del municipio."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_filters(self, request):
        serializer = ServiceFilterSerializer(
            data=request.query_params
        )
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        return ServiceFilters(
            clients=data.get("client", []),
            capacity_min=data.get("capacity_min"),
            capacity_max=data.get("capacity_max"),
            municipalities=data.get("municipality", []),
            departments=data.get("department", []),
            products=data.get("product", []),
            plans=data.get("plan", []),
            product_families=data.get("product_family", []),
            subsegments=data.get("subsegment", []),
        )

class ClientOptionsViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    @action(detail=False, methods=["get"])
    def active(self, request):
        try:
            result = active_ser_service.get_clients_options()
            if not result["success"]:
                logger.error(
                    "Error al consultar opciones de clientes: %s.",
                    result.get("message", "Error desconocido"),
                    extra={
                        "username": request.user.username,
                        "user_id": request.user.id,
                    }
                )
                return Response(
                    {"detail": "No fue posible consultar los clientes."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            return Response(
                result["data"],
                status=status.HTTP_200_OK
            )
        except Exception:
            logger.exception(
                "Error inesperado al consultar opciones de clientes.",
                extra={
                    "username": request.user.username,
                    "user_id": request.user.id,
                }
            )
            return Response(
                {"detail": "No fue posible consultar los clientes."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ServiceOptionsViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    @action(detail=False, methods=["get"], url_path="options")
    def options(self, request):
        try:
            result = active_ser_service.get_services_options()
            if not result["success"]:
                logger.error(
                    "Error al consultar opciones de servicios: %s.",
                    result.get("message", "Error desconocido"),
                    extra={
                        "username": request.user.username,
                        "user_id": request.user.id,
                    }
                )
                return Response(
                    {"detail": "No fue posible consultar las opciones de servicios."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            return Response(
                result["data"],
                status=status.HTTP_200_OK
            )

        except Exception:
            logger.exception(
                "Error inesperado al consultar opciones de servicios.",
                extra={
                    "username": request.user.username,
                    "user_id": request.user.id,
                }
            )
            return Response(
                {"detail": "No fue posible consultar las opciones de servicios."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )