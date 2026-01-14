import time
from typing import List
from app.api.v1.schemas import OptimizeRequest, OptimizeResponse
from app.domain.models import Truck, Order
from app.utils.grouping import group_by_lane_and_hazmat
from app.domain.compatibility import is_subset_date_compatible
from app.core.exceptions import ValidationError
from app.core.logging import get_logger

logger = get_logger()

MAX_ORDERS = 22

def optimize_load(request: OptimizeRequest) -> OptimizeResponse:
    start_time = time.perf_counter()

    if len(request.orders) > MAX_ORDERS:
        raise ValidationError(f"Maximum {MAX_ORDERS} orders allowed")

    truck = Truck(**request.truck.dict())
    orders = [Order(**o.dict()) for o in request.orders]

    best_payout = 0
    best_ids: List[str] = []
    best_weight = 0
    best_volume = 0

    groups = group_by_lane_and_hazmat(orders)

    for group in groups:
        k = len(group)
        if k == 0:
            continue

        # Sort by pickup date for efficient compatibility checking
        sorted_group = sorted(group, key=lambda o: (o.pickup_date, o.delivery_date))
        
        # For large groups, check if dates are sequential (common case optimization)
        if k > 15:
            # Check if this is a sequential date pattern (non-overlapping dates)
            # Compatible requires latest_pickup < earliest_delivery (strict <)
            # So sequential means delivery_date < next pickup_date
            is_sequential = True
            for i in range(k - 1):
                if sorted_group[i].delivery_date < sorted_group[i + 1].pickup_date:
                    continue
                else:
                    is_sequential = False
                    break
            
            if is_sequential:
                # For sequential dates, only contiguous subsets are compatible
                # This reduces from O(2^n) to O(n^2)
                for start in range(k):
                    cum_weight = 0
                    cum_volume = 0
                    cum_payout = 0
                    
                    for end in range(start, k):
                        cum_weight += sorted_group[end].weight_lbs
                        cum_volume += sorted_group[end].volume_cuft
                        cum_payout += sorted_group[end].payout_cents
                        
                        if cum_weight > truck.max_weight_lbs or cum_volume > truck.max_volume_cuft:
                            break
                        
                        if cum_payout > best_payout:
                            best_payout = cum_payout
                            best_ids = [sorted_group[i].id for i in range(start, end + 1)]
                            best_weight = cum_weight
                            best_volume = cum_volume
            else:
                # Non-sequential: check if orders have touching dates (delivery == next pickup)
                # If so, only individual orders are compatible - O(n)
                all_touching = True
                for i in range(k - 1):
                    if sorted_group[i].delivery_date != sorted_group[i + 1].pickup_date:
                        all_touching = False
                        break
                
                if all_touching:
                    # Orders have touching dates - only single orders are compatible
                    for order in sorted_group:
                        if (order.weight_lbs <= truck.max_weight_lbs and 
                            order.volume_cuft <= truck.max_volume_cuft):
                            if order.payout_cents > best_payout:
                                best_payout = order.payout_cents
                                best_ids = [order.id]
                                best_weight = order.weight_lbs
                                best_volume = order.volume_cuft
                else:
                    # Complex overlapping: use limited beam search
                    top_n = min(18, k)
                    top_orders = sorted(sorted_group, key=lambda o: o.payout_cents, reverse=True)[:top_n]
                    
                    for mask in range(1, 1 << top_n):
                        total_weight = 0
                        total_volume = 0
                        total_payout = 0
                        subset = []
                        
                        for i in range(top_n):
                            if (mask >> i) & 1:
                                o = top_orders[i]
                                total_weight += o.weight_lbs
                                total_volume += o.volume_cuft
                                total_payout += o.payout_cents
                                subset.append(o)
                                
                                if total_weight > truck.max_weight_lbs or total_volume > truck.max_volume_cuft:
                                    break
                        else:
                            if (total_weight <= truck.max_weight_lbs and 
                                total_volume <= truck.max_volume_cuft and
                                is_subset_date_compatible(subset)):
                                if total_payout > best_payout:
                                    best_payout = total_payout
                                    best_ids = [o.id for o in subset]
                                    best_weight = total_weight
                                    best_volume = total_volume
        else:
            # For smaller groups, use full enumeration
            for mask in range(1, 1 << k):
                total_weight = 0
                total_volume = 0
                total_payout = 0
                subset_indices = []
                
                for i in range(k):
                    if (mask >> i) & 1:
                        o = sorted_group[i]
                        total_weight += o.weight_lbs
                        total_volume += o.volume_cuft
                        total_payout += o.payout_cents
                        subset_indices.append(i)
                        
                        if total_weight > truck.max_weight_lbs or total_volume > truck.max_volume_cuft:
                            break
                else:
                    if total_weight <= truck.max_weight_lbs and total_volume <= truck.max_volume_cuft:
                        if total_payout > best_payout:
                            subset = [sorted_group[i] for i in subset_indices]
                            if is_subset_date_compatible(subset):
                                best_payout = total_payout
                                best_ids = [o.id for o in subset]
                                best_weight = total_weight
                                best_volume = total_volume

    elapsed = time.perf_counter() - start_time

    logger.info(
        "optimize_load completed | orders=%d | groups=%d | best_payout=%d | time=%.4fs",
        len(orders),
        len(groups),
        best_payout,
        elapsed,
    )

    return OptimizeResponse(
        truck_id=truck.id,
        selected_order_ids=best_ids,
        total_payout_cents=best_payout,
        total_weight_lbs=best_weight,
        total_volume_cuft=best_volume,
        utilization_weight_percent=round(
            best_weight / truck.max_weight_lbs * 100, 2
        ) if truck.max_weight_lbs else 0.0,
        utilization_volume_percent=round(
            best_volume / truck.max_volume_cuft * 100, 2
        ) if truck.max_volume_cuft else 0.0,
    )
