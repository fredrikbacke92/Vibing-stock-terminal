from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class ETF:
    """Data model for an ETF with performance metrics."""
    ticker: str
    sector: str
    price: Optional[float] = None
    volume: Optional[float] = None
    performance: Dict[str, Optional[float]] = None

    def __post_init__(self):
        if self.performance is None:
            self.performance = {}