import redis
from config import UPSTASH_REDIS_URL
from database import db as database_instance 

try:
    redis_client = redis.from_url(UPSTASH_REDIS_URL, decode_responses=True)
    redis_client.ping()
    print("DEBUGING conexao do redis 100%")
except Exception as e:
    print(f"ERRO ao conectar ao redis: {e}")
    redis_client = None
db = database_instance
