from fastapi import APIRouter, BackgroundTasks

router = APIRouter()

@router.post("/notify/{token}")
def webhook_notify(token: str, background_tasks: BackgroundTasks):
    """Webhook通知の認証を無効化"""
    background_tasks.add_task(send_webhook, token)
    return {"msg": "Webhook scheduled"}

def send_webhook(token: str):
    """Webhook送信処理"""
    print(f"Webhook sent for {token}")
