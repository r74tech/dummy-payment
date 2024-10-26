import json
import requests

from fastapi import APIRouter, HTTPException, Header, Request, BackgroundTasks
from app.models import PaymentRequest, RefundRequest
from app.redis_utils import redis_client


router = APIRouter()

def store_transaction(token: str, transaction: dict):
    """Redisにトランザクションを保存（30分の有効期限付き）"""
    redis_client.setex(token, 1800, json.dumps(transaction))  # JSON形式で保存

def get_transaction(token: str):
    """Redisからトランザクションを取得"""
    data = redis_client.get(token)
    if data:
        return json.loads(data)  # JSON形式で取得
    return None

@router.post("/start")
def start_payment(request: PaymentRequest, access_token: str = Header(...)):
    """支払い開始エンドポイント"""
    transaction = {
        "status": "pending",
        "order_id": request.order_id,
        "amount": request.amount,
    }
    store_transaction(access_token, transaction)
    return {
        "msg": "Checkout initiated",
        "access_token": access_token,
        "status": "pending",
    }


@router.post("/capture/{token}")
def capture_payment(token: str, background_tasks: BackgroundTasks, request: Request):
    """Capture the payment and trigger the webhook"""
    transaction = get_transaction(token)

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    if transaction["status"] == "captured":
        return {"msg": "Payment already captured", "transaction": transaction}

    if transaction["status"] != "pending":
        raise HTTPException(status_code=400, detail="Invalid capture request.")

    # Update the transaction status to captured
    transaction["status"] = "captured"
    store_transaction(token, transaction)

    # **Corrected:** Use the incoming request headers to derive the correct host and port.
    scheme = request.headers.get("X-Forwarded-Proto", request.url.scheme)
    host = request.headers.get("Host", f"{request.client.host}:{request.url.port or 80}")

    callback_url = f"{scheme}://{host}/callback"

    # Schedule the webhook as a background task
    background_tasks.add_task(send_webhook, token, transaction, callback_url)

    return {"msg": "Payment captured", "transaction": transaction}


@router.post("/refund/{token}")
def refund_payment(token: str, refund: RefundRequest):
    """返金処理"""
    transaction = get_transaction(token)
    if not transaction or transaction["status"] != "captured":
        raise HTTPException(status_code=400, detail="Refund not allowed.")
    transaction["status"] = "refunded"
    store_transaction(token, transaction)
    return {"msg": "Refund successful", "transaction": transaction}

def send_webhook(token: str, transaction: dict, callback_url: str):
    """Webhook通知を指定のURLに送信"""
    payload = {"token": token, "transaction": transaction}
    try:
        print(f"Sending webhook for {token} to {callback_url}")
        response = requests.post(callback_url, json=payload)
        if response.status_code == 200:
            print(f"Webhook successfully sent for {token}")
            redis_client.set(token, "notified", ex=86400)
        else:
            print(f"Failed to send webhook for {token}: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error sending webhook: {e}")
        redis_client.incr(f"{token}:retries")
