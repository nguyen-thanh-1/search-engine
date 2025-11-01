import joblib
import os
from sklearn.metrics.pairwise import cosine_similarity

# Đường dẫn file (phải giống hệt file build_index.py)
DATA_DIR = 'data'
VECTORIZER_FILE = os.path.join(DATA_DIR, 'vectorizer.joblib')
MATRIX_FILE = os.path.join(DATA_DIR, 'tfidf_matrix.joblib')
DOCUMENTS_FILE = os.path.join(DATA_DIR, 'documents.joblib')
MAP_FILE = os.path.join(DATA_DIR, 'doc_id_map.joblib')


class SearchEngine:
    def __init__(self):
        """
        Khởi tạo Module 3: Tải các file chỉ mục đã được build.
        """
        print("--- Khởi tạo Module 3: Truy vấn & Xếp hạng ---")
        try:
            self.vectorizer = joblib.load(VECTORIZER_FILE)
            self.tfidf_matrix = joblib.load(MATRIX_FILE)
            self.documents = joblib.load(DOCUMENTS_FILE) # Đây là dict {id: doc}
            self.doc_id_map = joblib.load(MAP_FILE)     # Đây là dict {index: id}
            print("Tải chỉ mục và dữ liệu thành công.")
        except FileNotFoundError:
            print(f"LỖI: Không tìm thấy file chỉ mục trong '{DATA_DIR}'.")
            print("Vui lòng chạy file 'build_index.py' trước tiên.")
            # Thoát chương trình nếu không có chỉ mục
            exit()

    def search(self, query, top_k=10):
        """
        Thực hiện tìm kiếm và xếp hạng.
        """
        if not query.strip():
            return []

        # 1. Xử lý truy vấn
        # Dùng vectorizer.transform() để xử lý query
        # (nó sẽ tự động làm sạch y hệt lúc build chỉ mục)
        query_vector = self.vectorizer.transform([query])

        # 2. Tính độ tương đồng Cosine
        # So sánh vector truy vấn với TẤT CẢ các vector tài liệu
        cosine_scores = cosine_similarity(query_vector, self.tfidf_matrix).flatten()

        # 3. Xếp hạng
        # Lấy N chỉ số (indices) của các tài liệu có điểm cao nhất
        # argsort() sắp xếp từ thấp đến cao, [::-1] để đảo ngược
        top_indices = cosine_scores.argsort()[::-1][:top_k]

        # 4. Trả về kết quả
        results = []
        for idx in top_indices:
            score = cosine_scores[idx]
            
            # Chỉ lấy kết quả có điểm > 0
            if score == 0:
                continue

            # Lấy ID gốc từ chỉ số của ma trận
            doc_id = self.doc_id_map[idx]
            
            # Lấy thông tin tài liệu gốc từ dict
            doc = self.documents[doc_id]

            results.append({
                'id': doc_id,
                'title': doc['title'],
                'score': score,
                'category': doc.get('category', 'N/A'),
                'area': doc.get('area', 'N/A'),
                'image': doc.get('image', '')
            })
            
        return results