from dataclasses import dataclass

@dataclass (frozen=True)
class FinancialVariables:
    trm: float
    eth_output_mbps: float
    oym: float
    poles: float
    ducts: float
    call_center: float
    distribution: float
    collection: float
    web_capex: float
    margin_factor: float
    gmf: float
    fontic: float
    ica: float
    cartera: float
    monthly_wacc: float