from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class Truck:
    id: str
    max_weight_lbs: int
    max_volume_cuft: int

@dataclass(frozen=True)
class Order:
    id: str
    payout_cents: int
    weight_lbs: int
    volume_cuft: int
    origin: str
    destination: str
    pickup_date: date
    delivery_date: date
    is_hazmat: bool
