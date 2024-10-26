#!/bin/bash

API_URL="http://localhost:8001"
PAYMENT_SERVER_URL="http://localhost:8000"

# エラーハンドリングを有効にする
set -e

# Step 1: トークンの取得
echo "=== Step 1: Get Access Token ==="
TOKEN_RESPONSE=$(curl -s -X POST "$PAYMENT_SERVER_URL/auth/token")
ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token')

if [[ -z "$ACCESS_TOKEN" || "$ACCESS_TOKEN" == "null" ]]; then
  echo "Error: Failed to retrieve access token."
  exit 1
fi

echo "Access Token: $ACCESS_TOKEN"

# Step 2: カートに商品を追加
echo "=== Step 2: Add Item to Cart ==="
CART_RESPONSE=$(curl -s -X POST "$API_URL/cart/add" \
  -H "Content-Type: application/json" \
  -d '{"item_id": "item001", "quantity": 2, "price": 100.0}')

echo "Cart Response: $CART_RESPONSE"

# Step 3: チェックアウトの開始
echo "=== Step 3: Start Checkout ==="
CHECKOUT_RESPONSE=$(curl -s -X POST "$API_URL/checkout" \
  -H "Content-Type: application/json" \
  -H "access-token: $ACCESS_TOKEN" \
  -d '{"order_id": "order123"}')

echo "Checkout Response: $CHECKOUT_RESPONSE"
PAYMENT_TOKEN=$(echo "$CHECKOUT_RESPONSE" | jq -r '.access_token')

if [[ -z "$PAYMENT_TOKEN" || "$PAYMENT_TOKEN" == "null" ]]; then
  echo "Error: Failed to retrieve payment token."
  exit 1
fi

echo "Payment Token: $PAYMENT_TOKEN"

# Step 4: 支払いのキャプチャ
echo "=== Step 4: Capture Payment ==="
CAPTURE_RESPONSE=$(curl -s -X POST "$PAYMENT_SERVER_URL/payments/capture/$PAYMENT_TOKEN")
echo "Capture Response: $CAPTURE_RESPONSE"

# Step 5: Webhook通知の送信
echo "=== Step 5: Send Webhook Notification ==="
WEBHOOK_RESPONSE=$(curl -s -X POST "$PAYMENT_SERVER_URL/webhook/notify/$PAYMENT_TOKEN")
echo "Webhook Response: $WEBHOOK_RESPONSE"

echo "=== Payment Flow Completed Successfully ==="
