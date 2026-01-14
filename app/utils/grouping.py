from typing import List, Dict, Tuple
from app.domain.models import Order

def group_by_lane_and_hazmat(orders: List[Order]) -> List[List[Order]]:
    groups: Dict[Tuple[str, str, bool], List[Order]] = {}
    for o in orders:
        key = (o.origin.strip().lower(), o.destination.strip().lower(), o.is_hazmat)
        groups.setdefault(key, []).append(o)
    return list(groups.values())
