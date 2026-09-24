import django_filters
from . import models
from dataclasses import dataclass, field

class UUIDInFilter(django_filters.BaseInFilter, django_filters.UUIDFilter):
    pass

class MunicipalityFilter(django_filters.FilterSet):
    department = UUIDInFilter(field_name='department_id')
    class Meta:
        model = models.Municipality
        fields = ['department']

@dataclass
class PricingSiteFilters:
    period_value: int | None = None
    period_unit: str | None = None
    clients: list[str] = field(default_factory=list)
    funnels : list[str] = field(default_factory=list)
    funnel_statuses: list[str] = field(default_factory=list)
    capacity_min: float | None = None
    capacity_max: float | None = None
    departments: list[str] = field(default_factory=list)
    municipalities: list[str] = field(default_factory=list)
    danes: list[str] = field(default_factory=list)
    products: list[str] = field(default_factory=list)
    plans: list[str] = field(default_factory=list)
    product_families: list[str] = field(default_factory=list)
    page: int = 1
    page_size: int = 50

@dataclass
class PricingSiteFilterOptions:
    # Filtros que afectan la población
    period_value: int | None = None
    period_unit: str | None = None
    clients: list[str] = field(default_factory=list)
    funnel_statuses: list[str] = field(default_factory=list)
    capacity_min: float | None = None
    capacity_max: float | None = None
    departments: list[str] = field(default_factory=list)
    municipalities: list[str] = field(default_factory=list)
    danes: list[str] = field(default_factory=list)
    products: list[str] = field(default_factory=list)
    plans: list[str] = field(default_factory=list)
    product_families: list[str] = field(default_factory=list)