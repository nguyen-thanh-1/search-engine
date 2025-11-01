import os
from typing import List

import joblib
from sklearn.metrics.pairwise import cosine_similarity

from src.schemas.recipe_schemas import SearchResult
from src.app_config import app_config


class SearchEngine:
    def __init__(self):
        """
        Khởi tạo Module 3: Tải các file chỉ mục đã được build.
        """
        print("--- Initializing Search Engine ---")

        data_dir = app_config.DATA_DIR or "data"

        try:
            self.vectorizer = joblib.load(app_config.VECTORIZER_FILE_PATH)
            self.tfidf_matrix = joblib.load(app_config.MATRIX_FILE_PATH)
            self.documents = joblib.load(app_config.DOCUMENTS_FILE_PATH)
            doc_id_map_path = os.path.join(data_dir, "doc_id_map.joblib")
            self.doc_id_map = joblib.load(doc_id_map_path)
            print("Loaded index files successfully")
        except FileNotFoundError:
            print(f"ERROR: Index files not found in '{data_dir}'.")
            print("Please run indexing first.")
            exit()

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
        Search for recipes and return SearchResult objects
        """
        raw_results = self.search(query, top_k)
        return [SearchResult(**result) for result in raw_results]
