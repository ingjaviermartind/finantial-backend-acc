from dataclasses import dataclass

@dataclass
class MarketReference:
    source: str          # municipality | department | national
    sample_size: int
    median_price_mbps: float
    mean_price_mbps: float
    std_price_mbps: float