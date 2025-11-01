from typing import List

from pydantic import BaseModel


class CrawlRequest(BaseModel):
    keywords: List[str]
    categories: List[str] = []
    delay: int = 1
