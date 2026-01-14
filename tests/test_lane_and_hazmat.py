import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_lane_case_insensitive_and_hazmat_separation():
    # Two orders with same lane differing in case should be grouped together
    # But hazmat flag separates groups: hazmat order should not be combined with non-hazmat
    payload = {
        "truck": {"id": "t1", "max_weight_lbs": 10000, "max_volume_cuft": 1000},
        "orders": [
            {"id": "nh1", "payout_cents": 5000, "weight_lbs": 3000, "volume_cuft": 100,
             "origin": "Chicago", "destination": "Dallas", "pickup_date": "2026-01-01", "delivery_date": "2026-01-02", "is_hazmat": False},
            {"id": "NH2", "payout_cents": 6000, "weight_lbs": 3000, "volume_cuft": 100,
             "origin": "CHICAGO ", "destination": "dallas", "pickup_date": "2026-01-03", "delivery_date": "2026-01-04", "is_hazmat": False},
            {"id": "hz1", "payout_cents": 20000, "weight_lbs": 3000, "volume_cuft": 100,
             "origin": "Chicago", "destination": "Dallas", "pickup_date": "2026-01-05", "delivery_date": "2026-01-06", "is_hazmat": True}
        ]
    }
    r = client.post('/api/v1/load-optimizer/optimize', json=payload)
    assert r.status_code == 200
    data = r.json()
    # hazmat is separate group; best choice is hazmat single order since it has highest payout
    assert data['selected_order_ids'] == ['hz1']
    assert data['total_payout_cents'] == 20000
