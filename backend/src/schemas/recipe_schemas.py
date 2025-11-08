from typing import List, Optional

from pydantic import BaseModel


class Recipe(BaseModel):
    id: str
    title: str
    category: Optional[str] = None
    area: Optional[str] = None
    instructions: Optional[str] = None
    image: Optional[str] = None
    ingredients: List[str] = []


class SearchResult(BaseModel):
    id: str
    title: str
    score: float
    category: str
    area: str
    image: str
    snippet: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    category: Optional[str] = None
    area: Optional[str] = None
    ingredients: Optional[List[str]] = []
