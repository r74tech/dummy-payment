import json
from fastapi import APIRouter, HTTPException, Header
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
def capture_payment(token: str):
    """支払いのキャプチャ（確定）"""
    transaction = get_transaction(token)
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    # すでに 'captured' 状態ならば成功レスポンスを返す
    if transaction["status"] == "captured":
        return {"msg": "Payment already captured", "transaction": transaction}

    if transaction["status"] != "pending":
        raise HTTPException(status_code=400, detail="Invalid capture request.")

    # ステータスを 'captured' に更新
    transaction["status"] = "captured"
    store_transaction(token, transaction)

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
