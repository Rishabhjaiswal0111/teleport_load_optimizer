import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_basic_sample():
    with open('sample_requests/sample.json') as f:
        payload = json.load(f)
    r = client.post('/api/v1/load-optimizer/optimize', json=payload)
    assert r.status_code == 200
    data = r.json()
    assert 'truck_id' in data
    assert isinstance(data['selected_order_ids'], list)
