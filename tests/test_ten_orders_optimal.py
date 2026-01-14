import json
from fastapi.testclient import TestClient
from app.main import app
import heapq

client = TestClient(app)

def test_ten_orders_best_top7_by_capacity():
    # 10 orders, each weight 2000 => capacity 15000 allows 7 orders (7*2000=14000)
    payouts = [1000,2000,3000,4000,5000,6000,7000,8000,9000,10000]  # increasing payouts
    orders = []
    for i, p in enumerate(payouts):
        orders.append({
            "id": f"o{i+1}",
            "payout_cents": p,
            "weight_lbs": 2000,
            "volume_cuft": 10,
            "origin": "X",
            "destination": "Y",
            "pickup_date": f"2026-01-{2*i+1:02d}",
            "delivery_date": f"2026-01-{2*i+2:02d}",
            "is_hazmat": False
        })
    payload = {"truck": {"id": "t1", "max_weight_lbs": 15000, "max_volume_cuft": 1000}, "orders": orders}
    r = client.post('/api/v1/load-optimizer/optimize', json=payload)
    assert r.status_code == 200
    data = r.json()
    # best is sum of top 7 payouts (largest 7)
    top7 = heapq.nlargest(7, payouts)
    assert data['total_payout_cents'] == sum(top7)
    assert len(data['selected_order_ids']) == 7
