from pydantic import BaseModel
from typing import Dict, List, Optional, Union

class Holding(BaseModel):
    tradingsymbol: str
    quantity: int
    last_price: float
    average_price: float
    pnl: float
    day_change: float
    day_change_percentage: float
    value: float
    sector: str

class PortfolioSnapshot(BaseModel):
    total_value: float
    sector_allocation: Dict[str, float]
    holdings_count: int
    unrealized_pnl: float
    day_change: float
    day_change_percentage: float
    holdings: List[Holding]

class AIAnalysisResponse(BaseModel):
    analysis: Union[Dict, str]

class AIRequest(BaseModel):
    question: Optional[str] = None
