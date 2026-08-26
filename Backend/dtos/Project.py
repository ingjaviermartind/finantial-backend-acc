from dataclasses import dataclass

@dataclass
class Project: 
    capacity_mbps: float
    contract_time: int
    initial_income: float
    product_type: str
    product : str
    subsegment: str