import json
from fastapi import APIRouter, HTTPException
from app.redis_utils import redis_client

router = APIRouter()

def store_transaction(token: str, transaction: dict):
    """期限なしでRedisにトランザクションを保存"""
    redis_client.set(token, json.dumps(transaction))  # 期限なし

def get_transaction(token: str):
    """Redisからトランザクションを取得"""
    data = redis_client.get(token)
    if data:
        return json.loads(data)
    return None

@router.post("/start")
def start_payment(request: dict):  # 型指定を削除
    """入力検証を無効化"""
    transaction = {
        "status": "pending",
        "order_id": request.get("order_id"),
        "amount": request.get("amount"),
    }
    token = "STATIC-TOKEN"  # 固定トークンを使用
    store_transaction(token, transaction)
    return {"msg": "Checkout initiated", "access_token": token, "status": "pending"}

@router.post("/capture/{token}")
def capture_payment(token: str):
    """支払いのキャプチャ"""
    transaction = get_transaction(token)
    if not transaction or transaction["status"] != "pending":
        raise HTTPException(status_code=400, detail="Invalid capture request.")
    transaction["status"] = "captured"
    store_transaction(token, transaction)
    return {"msg": "Payment captured", "transaction": transaction}

@router.post("/refund/{token}")
def refund_payment(token: str):
    """返金処理"""
    transaction = get_transaction(token)
    if not transaction or transaction["status"] != "captured":
        raise HTTPException(status_code=400, detail="Refund not allowed.")
    transaction["status"] = "refunded"
    store_transaction(token, transaction)
    return {"msg": "Refund successful", "transaction": transaction}
