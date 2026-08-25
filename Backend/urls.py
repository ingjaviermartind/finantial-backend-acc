from django.contrib import admin
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r'prices', views.PriceViewSet, basename='prices')
# router.register(r'versions', views.VersionViewSet, basename='versions')
router.register(r'department', views.DepartmentViewSet, basename='department')
router.register(r'municipalities', views.MunicipalityViewSet, basename='municipalities')
router.register(r'services', views.ServicesViewSet, basename="services")
router.register(r'pricing', views.PricingViewSet, basename='pricing')
router.register(r'financial-variables', views.FinancialVariableViewSet, basename='financial-variables')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'change-password/',
        views.ChangePasswordView.as_view(),
    ),
    path("health/", views.health.as_view()),
]

#
# EOF
#