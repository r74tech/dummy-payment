from fastapi import APIRouter, BackgroundTasks
from app.redis_utils import redis_client

router = APIRouter()

@router.post("/notify/{token}")
def webhook_notify(token: str, background_tasks: BackgroundTasks):
    """Webhook通知のエンドポイント"""
    background_tasks.add_task(send_webhook, token)
    return {"msg": "Webhook scheduled"}

def send_webhook(token: str):
    """Webhook送信と再試行カウント"""
    try:
        print(f"Webhook sent for {token}")
        redis_client.set(token, "notified", ex=86400)  # 通知済みとして1日保持
    except Exception as e:
        retry_count = redis_client.incr(f"{token}:retries")
        print(f"Webhook retry {retry_count} failed for {token}")
        if retry_count >= 3:
            print(f"Max retries reached for {token}, giving up.")
