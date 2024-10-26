#!/bin/bash

API_URL="http://localhost:8001"
PAYMENT_SERVER_URL="http://localhost:8000"

set -e

echo "=== Step 1: Get Access Token ==="
ACCESS_TOKEN="STATIC-TOKEN"
echo "Access Token: $ACCESS_TOKEN"

echo "=== Step 2: Add Item to Cart ==="
CART_RESPONSE=$(curl -s -X POST "$API_URL/cart/add" \
  -H "Content-Type: application/json" \
  -d '{"item_id": "item001", "quantity": 2, "price": 100.0}')
echo "Cart Response: $CART_RESPONSE"

echo "=== Step 3: Start Checkout ==="
CHECKOUT_RESPONSE=$(curl -s -X POST "$API_URL/checkout" \
  -H "Content-Type: application/json" \
  -d '{"order_id": "order123"}')
echo "Checkout Response: $CHECKOUT_RESPONSE"

PAYMENT_TOKEN=$(echo "$CHECKOUT_RESPONSE" | jq -r '.access_token')
echo "Payment Token: $PAYMENT_TOKEN"

echo "=== Step 4: Capture Payment ==="
CAPTURE_RESPONSE=$(curl -s -X POST "$PAYMENT_SERVER_URL/payments/capture/$PAYMENT_TOKEN")
echo "Capture Response: $CAPTURE_RESPONSE"

# 同じトークンに対して複数回返金を試行
echo "=== Refund Attempts ==="
for i in {1..10}; do
  RESPONSE=$(curl -s -X POST "$PAYMENT_SERVER_URL/payments/refund/$PAYMENT_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"amount": 100.0}')
  echo "Refund Attempt $i: $RESPONSE"
done
