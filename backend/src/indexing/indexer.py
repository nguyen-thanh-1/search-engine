import json
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

from src.app_config import app_config


class Indexer:
    
    def __init__(self):
        self.vectorizer = None
        self.tfidf_matrix = None
        self.documents = None
        self.doc_id_map = None
    
    def load_documents(self):
        if not app_config.JSON_FILE_PATH:
            raise ValueError("JSON_FILE_PATH not configured")
        
        with open(app_config.JSON_FILE_PATH, "r", encoding="utf-8") as f:
            documents = json.load(f)
        
        print(f"Đã tải {len(documents)} tài liệu")
        return documents
    
    def process_documents(self, documents):
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
        return processed_docs, doc_id_map
    
    def build_tfidf_index(self, processed_docs):
        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
        self.tfidf_matrix = self.vectorizer.fit_transform(processed_docs)
        print(f"Kích thước ma trận TF-IDF: {self.tfidf_matrix.shape}")
    
    def save_index(self, documents, doc_id_map):
        documents_dict = {doc["id"]: doc for doc in documents}
        joblib.dump(self.vectorizer, app_config.VECTORIZER_FILE_PATH)
        joblib.dump(self.tfidf_matrix, app_config.MATRIX_FILE_PATH)
        joblib.dump(documents_dict, app_config.DOCUMENTS_FILE_PATH)
        joblib.dump(doc_id_map, app_config.DOC_ID_MAP_FILE_PATH)
        print("Chỉ mục được lưu thành công")
    
    def index_recipes(self):
        """
        1. Tải dữ liệu từ JSON.
        2. Xử lý & áp dụng trọng số cho các trường (title, ingredients...).
        3. Build chỉ mục TF-IDF.
        4. Lưu chỉ mục và dữ liệu ra file.
        """
        documents = self.load_documents()
        processed_docs, doc_id_map = self.process_documents(documents)
        self.build_tfidf_index(processed_docs)
        self.save_index(documents, doc_id_map)
        return len(documents)


