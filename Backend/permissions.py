from rest_framework.permissions import BasePermission


ADMIN = "admin"
PRICING = "pricing"
EVALUADOR = "evaluador"
CONSULTA = "consulta"


class IsInGroup(BasePermission):
    groups = ()

    def has_permission(self, request, view):
        user = request.user

        return (
            user.is_authenticated
            and user.groups.filter(name__in=self.groups).exists()
        )


class IsAdmin(IsInGroup):
    groups = (ADMIN,)


class IsPricing(IsInGroup):
    groups = (PRICING,)


class IsPricingOrAdmin(IsInGroup):
    groups = (PRICING, ADMIN)


class CanEvaluate(IsInGroup):
    groups = (PRICING, ADMIN, EVALUADOR)


class CanViewDetailedResults(IsInGroup):
    groups = (PRICING, ADMIN)


class CanRequestPricingReview(IsInGroup):
    groups = (EVALUADOR,)


class CanManageFinancialVariables(IsInGroup):
    groups = (PRICING, ADMIN)

def can_view_detailed_results(user):
    return (
        user.is_authenticated
        and user.groups.filter(
            name__in=(ADMIN, PRICING)
        ).exists()
    )