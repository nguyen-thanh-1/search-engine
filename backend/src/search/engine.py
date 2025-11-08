import os
import re
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

    def _generate_snippet(self, doc_id: str, query: str) -> str:
        """Tạo đoạn trích ngắn từ hướng dẫn nấu ăn (instructions) với từ khóa được highlight"""
        doc = self.documents.get(doc_id, {})
        full_text = doc.get('instructions', '')  # Lấy phần hướng dẫn nấu ăn
        
        if not full_text:
            return doc.get('title', '')
        
        # Tách thành các từ
        tokens = re.findall(r'\b\w+\b', full_text)
        query_terms = set(re.findall(r'\b\w+\b', query.lower()))
        
        # Tìm từ khóa đầu tiên trong hướng dẫn
        for i, token in enumerate(tokens):
            if token.lower() in query_terms:
                # Lấy 10 từ trước và sau làm context
                start = max(0, i - 10)
                end = min(len(tokens), i + 10)
                snippet = tokens[start:end]
                # Highlight từ khóa
                snippet[i - start] = f"<b>{snippet[i - start]}</b>"
                return " ".join(snippet) + "..."
        
        # Không tìm thấy -> trả về 25 từ đầu
        return " ".join(tokens[:25]) + "..."

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
                    "snippet": self._generate_snippet(doc_id, query),
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
                    "snippet": self._generate_snippet(doc_id, " ".join(ingredients)),
                })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return [SearchResult(**result) for result in results[:top_k]]
