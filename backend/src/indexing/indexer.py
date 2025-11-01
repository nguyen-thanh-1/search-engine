import json

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

from src.app_config import app_config


def load_documents():
    """Load documents from JSON file."""
    if not app_config.JSON_FILE_PATH:
        raise ValueError("JSON_FILE_PATH not configured")

    with open(app_config.JSON_FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def run_indexing():
    """
    1. Tải dữ liệu từ JSON.
    2. Xử lý & áp dụng trọng số cho các trường (title, ingredients...).
    3. Build chỉ mục TF-IDF.
    4. Lưu chỉ mục và dữ liệu ra file.
    """
    documents = load_documents()
    print(f"Loaded {len(documents)} documents")

    processed_docs = []
    doc_id_map = {}

    for i, doc in enumerate(documents):
        title = (doc.get("title", "") + " ") * 3
        category = (doc.get("category", "") + " ") * 2
        area = (doc.get("area", "") + " ") * 2

        ingredients_list = doc.get("ingredients", [])
        ingredients = (", ".join(ingredients_list) + " ") * 2

        instructions = doc.get("instructions", "")

        combined_text = title + category + area + ingredients + instructions
        processed_docs.append(combined_text)

        doc_id_map[i] = doc["id"]

    print(f"Đã xử lý và áp dụng trọng số cho {len(processed_docs)} tài liệu.")

    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(processed_docs)

    print(f"Kích thước ma trận TF-IDF: {tfidf_matrix.shape}")

    joblib.dump(vectorizer, app_config.VECTORIZER_FILE_PATH)
    joblib.dump(tfidf_matrix, app_config.MATRIX_FILE_PATH)

    documents_dict = {doc["id"]: doc for doc in documents}
    joblib.dump(documents_dict, app_config.DOCUMENTS_FILE_PATH)

    # Save doc_id_map using data_dir from app_config
    doc_id_map_path = os.path.join(app_config.DATA_DIR, "doc_id_map.joblib") if app_config.DATA_DIR else "data/doc_id_map.joblib"
    joblib.dump(doc_id_map, doc_id_map_path)

    print(f"Saved index files to {app_config.DATA_DIR}")

