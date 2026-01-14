import json
from fastapi.testclient import TestClient
from app.main import app
import time

client = TestClient(app)

def test_extreme_22_all_selected_if_capacity_allows():
    orders = []
    total_payout = 0
    for i in range(22):
        orders.append({
            "id": f"o{i+1}",
            "payout_cents": 1000 + i*10,
            "weight_lbs": 100,   # small weight so all can fit
            "volume_cuft": 1,
            "origin": "L",
            "destination": "M",
            "pickup_date": f"2026-01-{i+1:02d}",
            "delivery_date": f"2026-01-{i+1+1:02d}",
            "is_hazmat": False
        })
        total_payout += (1000 + i*10)
    payload = {"truck": {"id": "t_extreme", "max_weight_lbs": 50000, "max_volume_cuft": 10000}, "orders": orders}
    t0 = time.perf_counter()
    r = client.post('/api/v1/load-optimizer/optimize', json=payload)
    duration = time.perf_counter() - t0
    assert r.status_code == 200
    data = r.json()
    # if dates are sequential without overlap and capacity allows, expect all orders selected
    assert set(data['selected_order_ids']) == set([o['id'] for o in orders])
    assert data['total_payout_cents'] == total_payout
    # ensure optimization didn't take excessively long in test environment
    assert duration < 10.0
