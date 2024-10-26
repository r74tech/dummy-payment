#!/bin/bash

API_URL="http://localhost:8001"
PAYMENT_SERVER_URL="http://localhost:8000"

# エラーハンドリングを有効にする
set -e

# 共通関数: APIレスポンスのエラーチェック
check_response() {
  local response="$1"
  local error_msg="$2"

  if [[ $(echo "$response" | jq -r '.detail // empty') != "" ]]; then
    echo "Error: $error_msg"
    echo "Response: $response"
    exit 1
  fi
}

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
check_response "$CART_RESPONSE" "Failed to add item to cart"
echo "Cart Response: $CART_RESPONSE"

echo "=== Step 3: Start Checkout ==="
CHECKOUT_RESPONSE=$(curl -s -X POST "$API_URL/checkout" \
  -H "access-token: $ACCESS_TOKEN")
check_response "$CHECKOUT_RESPONSE" "Failed to complete checkout"
ORDER_ID=$(echo "$CHECKOUT_RESPONSE" | jq -r '.order_id')
PAYMENT_TOKEN=$(echo "$CHECKOUT_RESPONSE" | jq -r '.access_token')

echo "Order ID: $ORDER_ID"
echo "Payment Token: $PAYMENT_TOKEN"

