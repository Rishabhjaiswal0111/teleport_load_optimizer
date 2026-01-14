# Sample Requests for SmartLoad API

Each JSON file corresponds to a specific test scenario.
JSON does not support comments, so explanations are documented here.

---

## 01_date_overlap_same_day.json
**Purpose:**
- Tests overlapping date handling.
- delivery_date of o1 == pickup_date of o2.
- Expected: Orders cannot be combined; optimizer should pick the higher payout single order.

---

## 02_ten_orders_optimal.json
**Purpose:**
- 10 orders with same lane and non-overlapping dates.
- Truck capacity allows only 7 orders.
- Expected: Select the 7 highest payout orders.

---

## 03_lane_case_and_hazmat.json
**Purpose:**
- Tests lane matching with case-insensitive city names.
- Tests hazmat isolation.
- Expected: Hazmat order evaluated separately; highest payout hazmat order selected.

---

## 04_extreme_22_orders.json
**Purpose:**
- Stress test with 22 orders in a single group.
- Dates are sequential and non-overlapping.
- Capacity allows all orders.
- Expected: All 22 orders selected; logs show execution time.

---

## How to use
```bash
curl -X POST http://127.0.0.1:8000/api/v1/load-optimizer/optimize           -H "Content-Type: application/json"           -d @01_date_overlap_same_day.json
```
