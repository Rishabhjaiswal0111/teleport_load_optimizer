from typing import List
from app.domain.models import Order

def is_subset_date_compatible(orders):
    if not orders:
        return True

    latest_pickup = max(o.pickup_date for o in orders)
    earliest_delivery = min(o.delivery_date for o in orders)

    return latest_pickup < earliest_delivery

