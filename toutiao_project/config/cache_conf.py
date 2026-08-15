from typing import Any

import redis.asyncio as redis
from pydantic import json

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# 创建 Redis 的连接对象
redis_client = redis.Redis(
    host=REDIS_HOST,    # Redis 服务器主机地址
    port=REDIS_PORT,    # Redis 端口号
    db=REDIS_DB,    # Redis 数据库编号
    decode_responses=True    # 是否将字节数据解码为字符串
)


# 读取字符串类型缓存
async def get_cache(key: str):
    try:
        await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败:{e}")
        return None


# 读取字典或列表类型缓存
async def get_json_cache(key: str):
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"获取json类型缓存失败:{e}")
        return None


# 设置缓存
async def set_cache(key: str, value: Any, expire: int = 3600):
    try:
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        await redis_client.setex(key, expire, value)
        return True
    except Exception as e:
        print(f"设置缓存失败:{e}")
        return None
    