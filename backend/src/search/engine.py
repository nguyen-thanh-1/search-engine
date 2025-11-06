import os
from typing import List

import joblib
from sklearn.metrics.pairwise import cosine_similarity

from src.schemas.recipe_schemas import SearchResult
from src.app_config import app_config


class SearchEngine:
    def __init__(self):
        self.vectorizer = joblib.load(app_config.VECTORIZER_FILE_PATH)
        self.tfidf_matrix = joblib.load(app_config.MATRIX_FILE_PATH)
        self.documents = joblib.load(app_config.DOCUMENTS_FILE_PATH)
        self.doc_id_map = joblib.load(app_config.DOC_ID_MAP_FILE_PATH)

    def search(self, query, top_k=10):
        """
        Thực hiện tìm kiếm và xếp hạng.
        """
        if not query.strip():
            return []

        query_vector = self.vectorizer.transform([query])
        cosine_scores = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        top_indices = cosine_scores.argsort()[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = cosine_scores[idx]

            if score == 0:
                continue

            doc_id = self.doc_id_map[idx]
            doc = self.documents[doc_id]

            results.append(
                {
                    "id": doc_id,
                    "title": doc["title"],
                    "score": score,
                    "category": doc.get("category", "N/A"),
                    "area": doc.get("area", "N/A"),
                    "image": doc.get("image", ""),
                }
            )

        return results

    def search_recipes(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """
        Tìm kiếm công thức và trả về danh sách các SearchResult
        """
        raw_results = self.search(query, top_k)
        return [SearchResult(**result) for result in raw_results]

    def search_by_ingredients(self, ingredients: List[str], top_k: int = 10) -> List[SearchResult]:
        ingredients_lower = [ing.lower() for ing in ingredients]
        results = []
        
        for doc_id, doc in self.documents.items():
            doc_ingredients = doc.get("ingredients", [])
            doc_ingredients_lower = [ing.lower() for ing in doc_ingredients]
            
            matches = sum(1 for ingredient in ingredients_lower 
                         if any(ingredient in doc_ing for doc_ing in doc_ingredients_lower))
            
            if matches > 0:
                score = matches / len(ingredients_lower)
                results.append({
                    "id": doc_id,
                    "title": doc["title"],
                    "score": score,
                    "category": doc.get("category", "N/A"),
                    "area": doc.get("area", "N/A"),
                    "image": doc.get("image", ""),
                })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return [SearchResult(**result) for result in results[:top_k]]
