from Backend.dtos.Project import Project
from Backend.dtos.FinancialVariables import FinancialVariables

from Backend.services.financial_engine import financial_engine

class PricingOptimizer:
    @staticmethod
    def find_intervals(project : Project, variables : FinancialVariables, initial_sensitivity = 1.0, min_sensitivity = 1e-6, max_sen = 100):
        sens = initial_sensitivity
        results = financial_engine.evaluate_project(
            project,
            variables,
            sensitivity=sens
        )
        if results.approved:
            high = sens
            while sens <= max_sen:
                next_sens = sens / 2
                if next_sens < min_sensitivity:
                    break
                results = financial_engine.evaluate_project(
                    project,
                    variables,
                    sensitivity=next_sens
                )
                if not results.approved:
                    return next_sens, sens
                sens = next_sens
            return min_sensitivity, high
        # caso b
        low = sens
        while sens <= max_sen:
            sens *= 2
            results = financial_engine.evaluate_project(
                project,
                variables,
                sensitivity=sens
            )
            if results.approved:
                return low, sens
            low = sens

    @staticmethod
    def find_floor(project : Project, variables : FinancialVariables, tolerance=1e-4, max_iter=100):
        low, high = PricingOptimizer.find_intervals(project, variables)
        best = None
        for _ in range(max_iter):
            mid = (low+high)/2
            result = financial_engine.evaluate_project(project, variables, sensitivity=mid)
            if result.approved:
                result.sensitivity = mid
                best = result
                high = mid
            else:
                low = mid
            if abs(high-low) < tolerance:
                break
        if best is None:
            raise ValueError(
                "La búsqueda binaria no encontró una solución válida."
            )
        return best

