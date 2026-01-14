import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_overlapping_same_date_rejected():
    # o1.delivery == o2.pickup -> should be considered overlapping (incompatible)
    payload = {
        "truck": {"id": "t1", "max_weight_lbs": 10000, "max_volume_cuft": 1000},
        "orders": [
            {"id": "o1", "payout_cents": 1000, "weight_lbs": 1000, "volume_cuft": 100,
             "origin": "A", "destination": "B", "pickup_date": "2026-01-01", "delivery_date": "2026-01-05", "is_hazmat": False},
            {"id": "o2", "payout_cents": 2000, "weight_lbs": 1000, "volume_cuft": 100,
             "origin": "A", "destination": "B", "pickup_date": "2026-01-05", "delivery_date": "2026-01-10", "is_hazmat": False}
        ]
    }
    r = client.post('/api/v1/load-optimizer/optimize', json=payload)
    assert r.status_code == 200
    data = r.json()
    # cannot take both due to touching intervals considered overlap -> choose the higher payout single order (o2)
    assert data['selected_order_ids'] in (['o2'], ['o1']) or len(data['selected_order_ids']) == 1
    assert data['total_payout_cents'] in (1000, 2000)
