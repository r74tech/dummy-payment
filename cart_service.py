from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict
import requests

app = FastAPI()

cart: Dict[str, dict] = {}

class CartItem(BaseModel):
    item_id: str
    quantity: int
    price: float

class CheckoutRequest(BaseModel):
    order_id: str

PAYMENT_SERVER_URL = "http://localhost:8000"

@app.post("/cart/add")
def add_to_cart(item: CartItem):
    """カートに商品を追加"""
    cart[item.item_id] = {"quantity": item.quantity, "price": item.price}
    return {"msg": f"Item {item.item_id} added to cart", "cart": cart}

@app.post("/checkout")
def checkout(request: CheckoutRequest, background_tasks: BackgroundTasks):
    """CSRF保護なしで決済開始"""
    total_amount = sum(item["quantity"] * item["price"] for item in cart.values())

    response = requests.post(
        f"{PAYMENT_SERVER_URL}/payments/start",
        json={"order_id": request.order_id, "amount": total_amount}
    )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Payment initiation failed")

    payment_token = response.json().get("access_token")
    background_tasks.add_task(capture_payment, payment_token)

    return {"msg": "Checkout initiated", "access_token": payment_token, "amount": total_amount}

def capture_payment(token: str):
    """支払いのキャプチャ"""
    response = requests.post(f"{PAYMENT_SERVER_URL}/payments/capture/{token}")
    if response.status_code == 200:
        print(f"Payment captured successfully: {token}")
    else:
        print(f"Payment capture failed for token: {token}")
