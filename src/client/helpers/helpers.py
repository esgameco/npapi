import re
import functools
import asyncio

from typing import Optional

class NPHelpers:
    @staticmethod
    def contains(regex: str, msg: str) -> bool:
        return msg.find(regex) >= 0
    
    @staticmethod
    def search(regex: str, msg: str) -> Optional[str]:
        r = re.compile(regex, re.DOTALL)
        result = r.search(msg)
        if not result:
            return None
        return result
    
def retry_decorator(max_retries=3, delay=1):
    def decorator(function):
        @functools.wraps(function)
        async def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return await function(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    print(f"Attempt {retries} failed with exception: {e}")
                    if retries < max_retries:
                        await asyncio.sleep(delay)
                    else:
                        raise e
        return wrapper
    return decorator