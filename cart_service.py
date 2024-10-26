from fastapi import FastAPI, HTTPException, BackgroundTasks, Header
from pydantic import BaseModel
from typing import Dict
import requests

app = FastAPI()

# カート情報を保存する辞書
cart: Dict[str, dict] = {}

# リクエスト用モデル
class CartItem(BaseModel):
    item_id: str
    quantity: int
    price: float

class CheckoutRequest(BaseModel):
    order_id: str

# 決済エミュレータのエンドポイント
PAYMENT_SERVER_URL = "http://localhost:8000"

@app.post("/cart/add")
def add_to_cart(item: CartItem):
    """カートに商品を追加"""
    cart[item.item_id] = {"quantity": item.quantity, "price": item.price}
    return {"msg": f"Item {item.item_id} added to cart", "cart": cart}

@app.post("/checkout")
def checkout(request: CheckoutRequest, access_token: str = Header(...)):
    """チェックアウトと即時キャプチャの開始"""
    total_amount = sum(item["quantity"] * item["price"] for item in cart.values())

    # 決済サーバーに支払いリクエストを送信
    response = requests.post(
        f"{PAYMENT_SERVER_URL}/payments/start",
        json={"order_id": request.order_id, "amount": total_amount},
        headers={"access-token": access_token}
    )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Payment initiation failed")

    payment_token = response.json().get("access_token")

    if not payment_token:
        raise HTTPException(status_code=500, detail="Failed to retrieve payment token")

    # ここでキャプチャを直接呼び出す
    capture_response = capture_payment(payment_token)

    return {
        "msg": "Checkout and capture completed",
        "access_token": payment_token,
        "amount": total_amount,
        "capture_response": capture_response
    }

def capture_payment(token: str):
    """支払いをキャプチャする"""
    response = requests.post(f"{PAYMENT_SERVER_URL}/payments/capture/{token}")
    if response.status_code == 200:
        return {"msg": "Payment captured", "token": token}
    else:
        raise HTTPException(status_code=400, detail="Invalid capture request.")


@app.post("/webhook/receive")
def receive_webhook(data: dict):
    """Webhook通知を受け取る"""
    print(f"Received Webhook: {data}")
    return {"msg": "Webhook received successfully"}
