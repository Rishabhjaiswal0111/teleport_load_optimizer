#!/usr/bin/env python3
"""Quick validation of the optimization logic"""

# Simulate the sequential check
orders_data = [
    {"pickup": "2026-03-01", "delivery": "2026-03-02"},
    {"pickup": "2026-03-02", "delivery": "2026-03-03"},
    {"pickup": "2026-03-03", "delivery": "2026-03-04"},
]

# Check sequential pattern
is_sequential = True
for i in range(len(orders_data) - 1):
    if orders_data[i]["delivery"] > orders_data[i + 1]["pickup"]:
        is_sequential = False
        break

print(f"Sequential pattern detected: {is_sequential}")
print(f"For {len(orders_data)} orders:")
print(f"  - Brute force would check: 2^{len(orders_data)} = {2**len(orders_data)} combinations")
print(f"  - Optimized checks: {len(orders_data)}^2 = {len(orders_data)**2} combinations")

# For 22 orders
n = 22
print(f"\nFor 22 orders:")
print(f"  - Brute force: 2^{n} = {2**n:,} combinations")
print(f"  - Optimized: {n}^2 = {n**2} combinations")
print(f"  - Speedup: {(2**n) / (n**2):.0f}x faster")
