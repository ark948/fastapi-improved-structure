from typing import Annotated
from fastapi import Depends
from redis import Redis
from redis import asyncio as async_redis
from source.config import settings
import random




# User verification mechanism:
# Upon successful registration, a random 7 digit number will be generated and displayed for user (or emailed to user)
# that otp and user id will be stored in redis, with otp be the key
# if within 10 minutes, user enters the otp in specified link,
# redis client, will accept the otp and if is valid, will return the user id
# if user id is as same is the current user, user will be activated


# ONLY log errors or if something failed



USER_VERIFICATION_EXPIRY = 600



def redis_logger(func):
    def wrapper(*args, **kwargs):
        print("-> Redis task.")
        result = func(*args, **kwargs)
        return result
    return wrapper




@redis_logger
async def submit_otp_for_user(otp: int, user_id: str, redis_client: async_redis.Redis) -> bool:
    try:
        await redis_client.set(name=otp, value=user_id, ex=USER_VERIFICATION_EXPIRY)
    except Exception as error:
        print("\nRedis TASK FAILED. --> ", str(error))
        return False
    return True




@redis_logger
async def verify_otp_for_user(otp_input: str, user_id_input: str, redis_client: async_redis.Redis) -> bool:
    try:
        user_id = await redis_client.get(otp_input)
        if user_id.decode("utf-8") == user_id_input:
            return True
    except Exception as error:
        print("\nRedis TASK FAILED. --> ", str(error))
        return False
    return False



async def get_redis():
    async with async_redis.Redis.from_url(settings.REDIS_URL) as client:
        yield client



RedisDep = Annotated[Redis, Depends(get_redis)]