from dataclasses import dataclass
from abc import ABC, abstractmethod


from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(kw_only=True)
class Project(ABC):
    contract_time: int
    initial_income: float = 0
    initial_capex: float = 0

    @abstractmethod
    def calculate_capex(self, variables) -> float:
        """Calcula el CAPEX propio del tipo de proyecto."""
        raise NotImplementedError

    @abstractmethod
    def calculate_opex(self, variables) -> float:
        """Calcula el OPEX mensual propio del proyecto."""
        raise NotImplementedError

    @abstractmethod
    def calculate_monthly_income(
        self,
        variables,
        capex: float,
        opex: float
    ) -> float:
        """Calcula el ingreso mensual del proyecto."""
        raise NotImplementedError

@dataclass(kw_only=True)
class TelcoProject(Project):
    capacity_mbps: float
    product_type: str
    product: str
    subsegment: str
    sensitivity: float = 1.0
    def calculate_capex(self, variables) -> float:
        web_capex = (
            self.capacity_mbps
            * self.contract_time
            * variables.trm
            * variables.web_capex
        )

        return web_capex + self.initial_capex
    def calculate_opex(self, variables) -> float:
        return (
            self.capacity_mbps
            * variables.trm
            * variables.eth_output_mbps
            + variables.call_center
            + variables.oym
            + variables.poles
            + variables.ducts * variables.trm
            + variables.distribution
            + variables.collection
        )
    def calculate_monthly_income(self, variables, capex: float, opex: float) -> float:
        price_monthly = (
            (capex + opex * self.contract_time)
            / self.contract_time
        ) * self.sensitivity * variables.margin_factor
        return round(price_monthly / 1000) * 1000

@dataclass
class ProjectEconomics:
    capex: float
    opex_monthly: float
    monthly_income: float
    contract_time: int
    initial_income: float


class ProjectEconomicsBuilder:
    @staticmethod
    def build(project: Project, variables) -> ProjectEconomics:
        capex = project.calculate_capex(variables)
        opex = project.calculate_opex(variables)
        monthly_income = project.calculate_monthly_income(
            variables,
            capex,
            opex
        )
        return ProjectEconomics(
            capex=capex,
            opex_monthly=opex,
            monthly_income=monthly_income,
            contract_time=project.contract_time,
            initial_income=project.initial_income
        )
# @dataclass
# class Project: 
#     capacity_mbps: float
#     contract_time: int
#     initial_income: float
#     product_type: str
#     product : str
#     subsegment: str
#     initial_capex : float