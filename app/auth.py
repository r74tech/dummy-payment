from fastapi import APIRouter
from app.models import Token
from app.redis_utils import redis_client

router = APIRouter()

HARDCODED_TOKEN = "STATIC-TOKEN"  # 固定トークンの導入

@router.post("/token", response_model=Token)
def get_token():
    """固定トークンを返す"""
    return Token(access_token=HARDCODED_TOKEN, token_type="bearer")

def validate_token(token: str) -> bool:
    """Redisからトークンの有効性を検証"""
    return redis_client.exists(token) == 1
