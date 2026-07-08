import django_filters
from . import models

class MunicipalityFilter(django_filters.FilterSet):

    department = django_filters.UUIDFilter(
        field_name='department_id'
    )

    class Meta:
        model = models.Municipality
        fields = ['department']