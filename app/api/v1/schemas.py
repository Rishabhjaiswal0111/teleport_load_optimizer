from pydantic import BaseModel, Field, validator
from datetime import date
from typing import List

class TruckSchema(BaseModel):
    id: str
    max_weight_lbs: int = Field(..., ge=0)
    max_volume_cuft: int = Field(..., ge=0)

class OrderSchema(BaseModel):
    id: str
    payout_cents: int = Field(..., ge=0)
    weight_lbs: int = Field(..., ge=0)
    volume_cuft: int = Field(..., ge=0)
    origin: str
    destination: str
    pickup_date: date
    delivery_date: date
    is_hazmat: bool

    @validator("delivery_date")
    def validate_dates(cls, v, values):
        if "pickup_date" in values and v < values["pickup_date"]:
            raise ValueError("delivery_date must be >= pickup_date")
        return v

class OptimizeRequest(BaseModel):
    truck: TruckSchema
    orders: List[OrderSchema]
    single_trip: bool = True

class OptimizeResponse(BaseModel):
    truck_id: str
    selected_order_ids: List[str]
    total_payout_cents: int
    total_weight_lbs: int
    total_volume_cuft: int
    utilization_weight_percent: float
    utilization_volume_percent: float
