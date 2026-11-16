from dataclasses import dataclass
from typing import Literal

MarketSource = Literal[
    "municipality",
    "department",
    "national",
]

@dataclass(frozen=True, slots=True)
class MarketReference:
    source: MarketSource          
    sample_size: int
    median_price_mbps: float
    mean_price_mbps: float
    std_price_mbps: float