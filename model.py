from pydantic import BaseModel, Field

class MarketData(BaseModel):
    event_title: str = Field(..., description="The title of the market data")
    question: str = Field(..., description="The question associated with the market data")
    asset_id: int = Field(..., description="The asset ID associated with the market data")
    data : list[dict] = Field(..., description="The market data in JSON format")