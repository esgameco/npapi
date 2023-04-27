#
#              _                     
#    /\  /\___| |_ __   ___ _ __ ___ 
#   / /_/ / _ \ | '_ \ / _ \ '__/ __|
#  / __  /  __/ | |_) |  __/ |  \__ \
#  \/ /_/ \___|_| .__/ \___|_|  |___/
#               |_|                  
#
#

import logging
import re
import functools
import asyncio
import json

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

    @staticmethod
    def get_between(data, first, last):
        return data.split(first)[1].split(last)[0]
    
    @staticmethod
    def regex_find_all(data, first, last):
        return re.findall(rf"{first}(.*?){last}", data.lower())
    
    @staticmethod
    async def get_json(res) -> Optional[str]:
        """Gets json from aiohttp responses
        
        Will only return json if there is json to return
        """
        try:
            msg = await res.text()
            return json.loads(NPHelpers._fix_text(msg))
        except Exception as e:
            logging.warning(f'(Helper get_json) {e}')
        return None

    @staticmethod
    def _get_json(msg: str) -> Optional[str]:
        """Gets json from aiohttp responses
        
        Will only return json if there is json to return
        """
        try:
            return json.loads(NPHelpers._fix_text(msg))
        except Exception as e:
            logging.warning(f'(Helper _get_json) {e}')
        return None
    
    @staticmethod
    def _fix_text(msg: str) -> Optional[str]:
        """Fixes text in messages that contain / or \\"""
        try:
            return msg.replace('\n', '').replace('\t', '').replace('\r', '') # .replace('\\', '')
        except Exception as e:
            logging.warning(f'(Helper _fix_text) {e}')
        return None
    
    @staticmethod
    async def get_text(res) -> Optional[str]:
        """Returns fixed text of a response"""
        try:
            msg = await res.text()
            fixed = NPHelpers._fix_text(msg)
            return fixed
        except Exception as e:
            logging.warning(f'(Helper get_text) {e}')
        return None
    
async def run_function(func, slp:float=0.5):
    # try:
    #     await asyncio.sleep(slp)
    #     res = await func
    #     return res
    # except Exception as e:
    #     print("Error:", e)
    #     return None
    await asyncio.sleep(slp)
    res = await func
    return res
    
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
                    logging.warning(f"Attempt {retries} failed with exception: {e}")
                    if retries < max_retries:
                        await asyncio.sleep(delay)
                    else:
                        raise e
        return wrapper
    return decorator