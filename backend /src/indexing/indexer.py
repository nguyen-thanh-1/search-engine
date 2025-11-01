import json
import os

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

from src.app_config import app_config


def run_indexing():
    """
    1. Tải dữ liệu từ JSON.
    2. Xử lý & áp dụng trọng số cho các trường (title, ingredients...).
    3. Build chỉ mục TF-IDF.
    4. Lưu chỉ mục và dữ liệu ra file.
    """
    # Create data directory if it doesn't exist
    if app_config.DATA_DIR and not os.path.exists(app_config.DATA_DIR):
        os.makedirs(app_config.DATA_DIR, exist_ok=True)

    try:
        with open(app_config.JSON_FILE, "r", encoding="utf-8") as f:
            documents = json.load(f)
    except FileNotFoundError:
        print(
            f"LỖI: Không tìm thấy file {app_config.JSON_FILE}. Hãy chắc chắn bạn đã để file này đúng chỗ."
        )
        return
    except json.JSONDecodeError:
        print(f"LỖI: File {app_config.JSON_FILE} không phải là file JSON hợp lệ.")
        return

    print(f"Đã tải {len(documents)} tài liệu từ '{app_config.JSON_FILE}'.")

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

    joblib.dump(vectorizer, app_config.VECTORIZER_FILE)
    joblib.dump(tfidf_matrix, app_config.MATRIX_FILE)

    documents_dict = {doc["id"]: doc for doc in documents}
    joblib.dump(documents_dict, app_config.DOCUMENTS_FILE)

    # Save doc_id_map using data_dir from app_config
    doc_id_map_path = os.path.join(app_config.DATA_DIR, "doc_id_map.joblib") if app_config.DATA_DIR else "data/doc_id_map.joblib"
    joblib.dump(doc_id_map, doc_id_map_path)

    print(f"Đã lưu các file chỉ mục vào thư mục '{app_config.DATA_DIR}'.")

