from dataclasses import dataclass
from abc import ABC, abstractmethod
from decimal import Decimal
from Backend.utils import ZERO, ONE, THOUSAND, to_decimal, thousands

@dataclass(kw_only=True)
class Project(ABC):
    contract_time: int
    initial_income: Decimal = ZERO
    initial_capex: Decimal = ZERO

    @abstractmethod
    def calculate_capex_breakdown(self,variables) -> dict[str, Decimal]:
        raise NotImplementedError

    @abstractmethod
    def calculate_opex_breakdown(self,variables) -> dict[str, Decimal]:
        raise NotImplementedError

    @abstractmethod
    def calculate_monthly_income(self, variables, capex: Decimal, opex: Decimal) -> Decimal:
        raise NotImplementedError

@dataclass(kw_only=True)
class TelcoProject(Project):
    capacity_mbps: Decimal
    product_type: str
    product: str
    subsegment: str
    sensitivity: Decimal = Decimal("1")

    def __post_init__(self):
        self.capacity_mbps = to_decimal(self.capacity_mbps)
        self.initial_income = to_decimal(self.initial_income)
        self.initial_capex = to_decimal(self.initial_capex)
        self.sensitivity = to_decimal(self.sensitivity)

    def calculate_capex_breakdown(self, variables):
        return {
            "web_capex": (
                self.capacity_mbps
                * self.contract_time
                * variables.trm
                * variables.web_capex
            ),
            "initial_capex": self.initial_capex
        }

    def calculate_opex_breakdown(self, variables):
        return {
            "eth_output": (
                self.capacity_mbps
                * variables.trm
                * variables.eth_output_mbps
            ),
            "call_center": variables.call_center,
            "oym": variables.oym,
            "poles": variables.poles,
            "ducts": variables.ducts * variables.trm,
            "distribution": variables.distribution,
            "collection": variables.collection
        }

    def calculate_monthly_income(self, variables, capex: Decimal, opex: Decimal) -> Decimal:
        price_monthly = ( (capex + opex * Decimal(self.contract_time)) / Decimal(self.contract_time) ) * self.sensitivity * variables.margin_factor
        return thousands(price_monthly)

@dataclass(kw_only=True)
class MultiTelcoProject(Project):
    products: list[TelcoProject]
    def __post_init__(self):
        self.initial_income = to_decimal(self.initial_income)
        self.initial_capex = to_decimal(self.initial_capex)
        if not self.products:
            raise ValueError("El proyecto debe contener al menos un producto.")
        if any(product.contract_time != self.contract_time for product in self.products):
            raise ValueError("Todos los productos deben tener el mismo tiempo contractual.")
        if any( product.initial_income != 0 or product.initial_capex != 0 for product in self.products):
            raise ValueError("Los valores iniciales deben asignarse al proyecto global.")
        
    @property
    def capacity_mbps(self):
        return sum(
            (product.capacity_mbps for product in self.products),
            ZERO
        )

    @staticmethod
    def _aggregate_breakdowns(breakdowns):
        result = {}
        for breakdown in breakdowns:
            for concept, value in breakdown.items():
                result[concept] = (
                    result.get(concept, ZERO) + to_decimal(value)
                )

        return result

    def calculate_capex_breakdown(self, variables):
        breakdown = self._aggregate_breakdowns([
            product.calculate_capex_breakdown(variables)
            for product in self.products
        ])
        breakdown["initial_capex"] = (
            breakdown.get("initial_capex", ZERO)
            + self.initial_capex
        )
        return breakdown

    def calculate_opex_breakdown(self, variables):
        return self._aggregate_breakdowns([
            product.calculate_opex_breakdown(variables)
            for product in self.products
        ])

    def calculate_monthly_income(self, variables, capex, opex):
        total_income = ZERO
        for product in self.products:
            product_capex = sum(
                product.calculate_capex_breakdown(variables).values(),
                ZERO
            )
            product_opex = sum(
                product.calculate_opex_breakdown(variables).values(),
                ZERO
            )
            total_income += product.calculate_monthly_income(
                variables,
                product_capex,
                product_opex
            )
        return total_income

@dataclass
class ProjectEconomics:
    capex_breakdown: dict[str, Decimal]
    opex_breakdown: dict[str, Decimal]
    capex: Decimal
    opex_monthly: Decimal
    monthly_income: Decimal
    contract_time: int
    initial_income: Decimal


class ProjectEconomicsBuilder:

    @staticmethod
    def build(project, variables):
        capex_breakdown = project.calculate_capex_breakdown(variables)
        opex_breakdown = project.calculate_opex_breakdown(variables)
        capex = sum(capex_breakdown.values(), ZERO)
        opex = sum(opex_breakdown.values(), ZERO)
        monthly_income = project.calculate_monthly_income(
            variables,
            capex,
            opex
        )
        return ProjectEconomics(
            capex_breakdown=capex_breakdown,
            opex_breakdown=opex_breakdown,
            capex=capex,
            opex_monthly=opex,
            monthly_income=monthly_income,
            contract_time=project.contract_time,
            initial_income=project.initial_income
        )
