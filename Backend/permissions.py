from rest_framework.permissions import BasePermission

class IsPricing(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name='pricing').exists()
        )

class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name='admin').exists()
        )

class IsPricingOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(
                name__in=["pricing", "admin"]
            ).exists()
        )
#
# EOF
#