from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from rest_framework_simplejwt.authentication import JWTAuthentication


from Backend.models import Municipality, Department, ProductCatalog, Subsegment
from Backend.serializers import MunicipalitySerializer, DepartmentSerializer, ProductCatalogSerializer, SubsegmentSerializer

from django.db.models import Exists, OuterRef

from django_filters.rest_framework import DjangoFilterBackend
from Backend.filters import MunicipalityFilter

class DepartmentViewSet(ModelViewSet):
    authentication_classes = [JWTAuthentication]
    municipalities_unprofitable = Municipality.objects.filter(
        department=OuterRef('pk'),
        unprofitable=True
    )
    # permission_classes = [IsAuthenticated]
    queryset = Department.objects.exclude(
        name__in=[
            'AMAZONAS',
            'ARCHIPIELAGO DE SAN ANDRES'
        ]
    ).annotate(
        unprofitable=Exists(municipalities_unprofitable)
    ).order_by('name')
    serializer_class = DepartmentSerializer

class MunicipalityViewSet(ModelViewSet):
    authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = Municipality.objects.all()
    serializer_class = MunicipalitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = MunicipalityFilter


class ProductCatalogViewSet(ReadOnlyModelViewSet):
    authentication_classes = [JWTAuthentication]
    queryset = ProductCatalog.objects.filter(is_active=True)
    serializer_class = ProductCatalogSerializer

class SubsegmentViewSet(ReadOnlyModelViewSet):
    authentication_classes = [JWTAuthentication]
    queryset = Subsegment.objects.filter(is_active=True)
    serializer_class = SubsegmentSerializer

