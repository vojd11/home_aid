from pydantic import BaseModel, HttpUrl
from typing import Optional, List


class StorePrice(BaseModel):
    """Single store price information"""
    store_name: str
    price: Optional[float] = None
    currency: str = "грн"
    link: Optional[HttpUrl] = None
    status: str  # "success", "not_found", "error"


class StorePricesResponse(BaseModel):
    """Response containing all store prices for a medication"""
    medication_id: int
    medication_name: str
    stores: List[StorePrice]
    total_stores: int
    last_updated: Optional[str] = None
