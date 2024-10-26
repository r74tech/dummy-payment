import redis

def get_redis_client():
    """Redisクライアントを取得する関数"""
    return redis.Redis(host='redis', port=6379, decode_responses=True)

# グローバルなRedisクライアントを保持（初期化は1回のみ）
redis_client = get_redis_client()
