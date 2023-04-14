import re

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