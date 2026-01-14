# SmartLoad Optimization API

A high-performance truck load optimization API that maximizes payout while respecting weight, volume, and date compatibility constraints.

## How to run

```bash
git clone git@github.com:Rishabhjaiswal0111/teleport_load_optimizer.git
cd teleport_load_optimizer
docker compose up --build
# → Service will be available at http://localhost:8080
```

Interactive API documentation: **http://localhost:8080/docs**

## Health check

```bash
curl http://localhost:8080/docs
```

## Example request

```bash
curl -X POST http://localhost:8080/api/v1/load-optimizer/optimize \
  -H "Content-Type: application/json" \
  -d @sample_requests/sample.json
```

## API Specification

**Endpoint:** `POST /api/v1/load-optimizer/optimize`

**Request Body:**
```json
{
  "truck": {
    "id": "truck_1",
    "max_weight_lbs": 50000,
    "max_volume_cuft": 10000
  },
  "orders": [
    {
      "id": "order_1",
      "payout_cents": 150000,
      "weight_lbs": 5000,
      "volume_cuft": 500,
      "origin": "Chicago",
      "destination": "New York",
      "pickup_date": "2026-01-15",
      "delivery_date": "2026-01-17",
      "is_hazmat": false
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "truck_id": "truck_1",
  "selected_order_ids": ["order_1"],
  "total_payout_cents": 150000,
  "total_weight_lbs": 5000,
  "total_volume_cuft": 500,
  "utilization_weight_percent": 10.0,
  "utilization_volume_percent": 5.0
}
```

**HTTP Status Codes:**
- **200 OK** - Successful optimization
- **400 Bad Request** - Invalid input (validation errors, max orders exceeded)
- **413 Payload Too Large** - Request body exceeds 1MB
- **422 Unprocessable Entity** - Malformed JSON
- **500 Internal Server Error** - Unexpected server error

## Money Handling

All monetary values are handled as **integer cents** (never float/double) to ensure precision:
- `payout_cents: int` - Order payout in cents
- `total_payout_cents: int` - Total payout in cents

## Architecture

```
app/
├── api/v1/          # FastAPI routes and Pydantic schemas
├── services/        # Business logic and optimization orchestration
├── domain/          # Domain models and compatibility rules
├── utils/           # Pure utility functions (grouping, etc.)
└── core/            # Exceptions, logging, configuration
```

### Key Design Decisions

1. **Layered Architecture** - Clear separation between API, service, and domain layers
2. **Pydantic Validation** - Strong typing and automatic validation at API boundary
3. **Integer Money** - All monetary values in cents for precision
4. **Optimized Algorithm** - O(n²) for sequential dates, O(n) for touching dates, O(2^n) fallback for complex cases
5. **Comprehensive Error Handling** - Proper HTTP status codes for all error scenarios

## Sample Requests

Available samples:
- `sample_requests/sample.json` - Basic optimization
- `sample_requests/sample_dates.json` - Date compatibility testing
- `sample_requests/04_extreme_22_orders.json` - Maximum load (22 orders)

## Docker Details

- **Base Image**: python:3.11-slim
- **Multi-stage Build**: Optimized for production
- **Non-root User**: Runs as `appuser` (UID 1000)
- **Port**: 8080
- **Health Check**: Automatic container health monitoring

## Business Rules

1. **Date Compatibility**: Orders can be combined only if `max(pickup_dates) < min(delivery_dates)`
2. **Weight Constraint**: Total weight ≤ truck max_weight_lbs
3. **Volume Constraint**: Total volume ≤ truck max_volume_cuft
4. **Lane Grouping**: Orders grouped by (origin, destination, hazmat) before optimization
5. **Maximum Orders**: Limited to 22 orders per request

## Performance

- **Sequential dates**: < 0.01s for 22 orders
- **Touching dates**: < 0.001s for 22 orders (O(n) optimization)
- **Complex cases**: < 1s for up to 18 orders
