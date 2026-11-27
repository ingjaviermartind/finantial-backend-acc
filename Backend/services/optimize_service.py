from dataclasses import replace
from decimal import Decimal
from Backend.dtos import FinancialVariables, TelcoProject
from Backend.services.financial_engine import financial_engine

from Backend.utils import ZERO, ONE, HUNDRED, to_decimal

class PricingOptimizer:

    @staticmethod
    def evaluate_sensitivity(project: TelcoProject, variables: FinancialVariables, sensitivity: Decimal):
        # Evalúa una copia del proyecto con una sensibilidad determinada.
        # No modifica el proyecto original.
        project_variant = replace(
            project,
            sensitivity=to_decimal(sensitivity)
        )
        return financial_engine.evaluate_project(
            project_variant,
            variables
        )

    @staticmethod
    def find_intervals(project : TelcoProject, variables : FinancialVariables, initial_sensitivity = ONE, min_sensitivity = Decimal("0.000001"), max_sensitivity = HUNDRED):
        sensitivity = to_decimal(initial_sensitivity)
        min_sensitivity = to_decimal(min_sensitivity)
        max_sensitivity = to_decimal(max_sensitivity)

        if not ZERO < min_sensitivity <= sensitivity <= max_sensitivity:
            raise ValueError("El intervalo de sensibilidades no es válido.")
        
        result = PricingOptimizer.evaluate_sensitivity(
            project,
            variables,
            sensitivity
        )
        if result.approved:

            high = sensitivity

            while sensitivity <= min_sensitivity:
                next_sensitivity = sensitivity / Decimal("2")
                if next_sensitivity < min_sensitivity:
                    break
                result = PricingOptimizer.evaluate_sensitivity(
                    project,
                    variables,
                    next_sensitivity
                )
                if not result.approved:
                    return next_sensitivity, sensitivity
                
                sensitivity = next_sensitivity
                high = sensitivity

            return min_sensitivity, high
        # caso b

        low = sensitivity
        while sensitivity <= max_sensitivity:
            sensitivity = sensitivity * Decimal("2")
            result = PricingOptimizer.evaluate_sensitivity(
                project,
                variables,
                sensitivity
            )
            if result.approved:
                return low, sensitivity
            
            low = sensitivity
            if sensitivity == max_sensitivity:
                break
            sensitivity = next_sensitivity
        raise ValueError(
            "No se encontró una sensibilidad aprobada "
            "dentro del límite máximo."
        )

    @staticmethod
    def find_floor(project : TelcoProject, variables : FinancialVariables, tolerance=Decimal("0.0001"), max_iter=100):
        low, high = PricingOptimizer.find_intervals(project, variables)
        tolerance = to_decimal(tolerance)
        best = PricingOptimizer.evaluate_sensitivity(
            project,
            variables,
            high
        )

        for _ in range(max_iter):
            mid = (low + high) / Decimal("2")
            result = PricingOptimizer.evaluate_sensitivity(
                project,
                variables,
                mid
            )
            if result.approved:
                best = result
                high = mid
            else:
                low = mid
            if abs(high-low) < tolerance:
                break
        return best

