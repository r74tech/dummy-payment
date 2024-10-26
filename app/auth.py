from fastapi import APIRouter
from app.models import Token
from app.redis_utils import redis_client
import random, string

router = APIRouter()

def generate_token() -> str:
    """12文字のランダムなトークンを生成"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

@router.post("/token", response_model=Token)
def get_token():
    """トークンを取得しRedisに保存するエンドポイント"""
    token = generate_token()
    redis_client.setex(token, 1800, "valid")  # トークンを30分間有効にする
    return Token(access_token=token, token_type="bearer")

def validate_token(token: str) -> bool:
    """Redisからトークンの有効性を検証"""
    return redis_client.exists(token) == 1
