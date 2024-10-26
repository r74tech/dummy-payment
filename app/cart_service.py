import random
import string
from fastapi import FastAPI, HTTPException, Header, Request
from pydantic import BaseModel
from typing import Dict, List
import requests

app = FastAPI()

# カート情報と注文を保存する辞書
current_cart: Dict[str, dict] = {}  # 現在のカート
orders: Dict[str, List[dict]] = {}  # 注文情報ごとのカート内容

class CartItem(BaseModel):
    item_id: str
    quantity: int
    price: float

class CheckoutRequest(BaseModel):
    order_id: str

# 決済エミュレータのエンドポイント
PAYMENT_SERVER_URL = "http://localhost:8000"

def generate_order_id() -> str:
    """12文字のランダムなorder_idを生成"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

@app.post("/cart/add")
def add_to_cart(item: CartItem):
    """カートに商品を追加"""
    current_cart[item.item_id] = {"quantity": item.quantity, "price": item.price}
    return {"msg": f"Item {item.item_id} added to cart", "cart": current_cart}

@app.post("/checkout")
def checkout(request: Request, access_token: str = Header(...)):
    """チェックアウト時に新しい注文を生成"""
    if not current_cart:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # 新しい order_id を生成し、カートの内容を保存
    order_id = generate_order_id()
    orders[order_id] = list(current_cart.values())  # 注文ごとにカートの内容を保存

    # 合計金額を計算
    total_amount = sum(item["quantity"] * item["price"] for item in orders[order_id])

    # 決済サーバーに支払いリクエストを送信
    response = requests.post(
        f"{PAYMENT_SERVER_URL}/payments/start",
        json={"order_id": order_id, "amount": total_amount},
        headers={"access-token": access_token}
    )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Payment initiation failed")

    payment_token = response.json().get("access_token")

    if not payment_token:
        raise HTTPException(status_code=500, detail="Failed to retrieve payment token")

    # チェックアウト完了後、カートをクリア
    current_cart.clear()

    # 支払いのキャプチャを実行
    capture_response = capture_payment(request, payment_token)

    return {
        "msg": "Checkout and capture completed",
        "order_id": order_id,
        "access_token": payment_token,
        "amount": total_amount,
        "capture_response": capture_response
    }

@app.post("/callback")
def receive_webhook(data: dict):
    """Receive webhook notification"""
    print(f"Received Webhook: {data}")
    return {"msg": "Webhook received successfully"}


def capture_payment(request: Request, token: str):
    """支払いをキャプチャする"""
    response = requests.post(f"{PAYMENT_SERVER_URL}/payments/capture/{token}", headers={"Host": f"{request.url.hostname}:{request.url.port or 80}"})
    if response.status_code == 200:
        return {"msg": "Payment captured", "token": token}
    else:
        raise HTTPException(status_code=400, detail="Invalid capture request")
