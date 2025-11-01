from pathlib import Path
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
        print("--- Khởi tạo Module 3: Truy vấn & Xếp hạng ---")

        # Get paths from app_config with fallbacks
        data_dir = Path(app_config.DATA_DIR) if app_config.DATA_DIR else Path("data")
        vectorizer_file = Path(app_config.VECTORIZER_FILE) if app_config.VECTORIZER_FILE else data_dir / "vectorizer.joblib"
        matrix_file = Path(app_config.MATRIX_FILE) if app_config.MATRIX_FILE else data_dir / "tfidf_matrix.joblib"
        documents_file = Path(app_config.DOCUMENTS_FILE) if app_config.DOCUMENTS_FILE else data_dir / "documents.joblib"
        map_file = data_dir / "doc_id_map.joblib"

        try:
            self.vectorizer = joblib.load(vectorizer_file)
            self.tfidf_matrix = joblib.load(matrix_file)
            self.documents = joblib.load(documents_file)
            self.doc_id_map = joblib.load(map_file)
            print("Tải chỉ mục và dữ liệu thành công.")
        except FileNotFoundError:
            print(f"LỖI: Không tìm thấy file chỉ mục trong '{data_dir}'.")
            print("Vui lòng chạy file 'build_index.py' trước tiên.")
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
