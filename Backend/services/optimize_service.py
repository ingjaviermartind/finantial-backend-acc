from dataclasses import replace

from Backend.dtos import FinancialVariables, TelcoProject
from Backend.services.financial_engine import financial_engine

class PricingOptimizer:

    @staticmethod
    def evaluate_sensitivity(project: TelcoProject, variables: FinancialVariables, sensitivity: float):
        # Evalúa una copia del proyecto con una sensibilidad determinada.
        # No modifica el proyecto original.
        project_variant = replace(
            project,
            sensitivity=sensitivity
        )
        return financial_engine.evaluate_project(
            project_variant,
            variables
        )

    @staticmethod
    def find_intervals(project : TelcoProject, variables : FinancialVariables, initial_sensitivity = 1.0, min_sensitivity = 1e-6, max_sen = 100):
        sens = initial_sensitivity
        result = PricingOptimizer.evaluate_sensitivity(
            project,
            variables,
            initial_sensitivity
        )
        if result.approved:
            high = sens
            while sens <= max_sen:
                next_sens = sens / 2
                if next_sens < min_sensitivity:
                    break
                result = PricingOptimizer.evaluate_sensitivity(
                    project,
                    variables,
                    next_sens
                )
                if not result.approved:
                    return next_sens, sens
                sens = next_sens
            return min_sensitivity, high
        # caso b
        low = sens
        while sens <= max_sen:
            sens *= 2
            result = PricingOptimizer.evaluate_sensitivity(
                project,
                variables,
                sens
            )
            if result.approved:
                return low, sens
            low = sens

    @staticmethod
    def find_floor(project : TelcoProject, variables : FinancialVariables, tolerance=1e-4, max_iter=100):
        low, high = PricingOptimizer.find_intervals(project, variables)
        best = None
        for _ in range(max_iter):
            mid = (low+high)/2
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
        if best is None:
            raise ValueError("La búsqueda binaria no encontró una solución válida.")
        return best

