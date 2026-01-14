import json
import time
from app.services.load_optimizer import optimize_load
from app.api.v1.schemas import OptimizeRequest

with open('sample_requests/04_extreme_22_orders.json', 'r') as f:
    data = json.load(f)

request = OptimizeRequest(**data)

start = time.perf_counter()
result = optimize_load(request)
elapsed = time.perf_counter() - start

print(f"Execution time: {elapsed:.4f} seconds")
print(f"Selected orders: {len(result.selected_order_ids)}")
print(f"Total payout: {result.total_payout_cents}")
print(f"Order IDs: {result.selected_order_ids}")
