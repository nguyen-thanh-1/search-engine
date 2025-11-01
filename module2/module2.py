import json
import os
import re
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

# Đường dẫn file
JSON_FILE = 'recipes_by_keywords.json'
DATA_DIR = 'data'
VECTORIZER_FILE = os.path.join(DATA_DIR, 'vectorizer.joblib')
MATRIX_FILE = os.path.join(DATA_DIR, 'tfidf_matrix.joblib')
DOCUMENTS_FILE = os.path.join(DATA_DIR, 'documents.joblib')

def run_indexing():
    """
    Thực hiện toàn bộ quá trình của Module 2:
    1. Tải dữ liệu từ JSON.
    2. Xử lý & áp dụng trọng số cho các trường (title, ingredients...).
    3. Build chỉ mục TF-IDF.
    4. Lưu chỉ mục và dữ liệu ra file.
    """
    print("--- Bắt đầu Module 2: Xây dựng Chỉ mục ---")

    # Tạo thư mục 'data' nếu chưa có
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # 1. Tải dữ liệu từ JSON (Module 1)
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            documents = json.load(f)
    except FileNotFoundError:
        print(f"LỖI: Không tìm thấy file {JSON_FILE}. Hãy chắc chắn bạn đã để file này đúng chỗ.")
        return
    except json.JSONDecodeError:
        print(f"LỖI: File {JSON_FILE} không phải là file JSON hợp lệ.")
        return
    
    print(f"Đã tải {len(documents)} tài liệu từ '{JSON_FILE}'.")

    processed_docs = []
    doc_id_map = {} # Map thứ tự của matrix (0, 1, 2...) với ID gốc ("52795"...)

    # 2. Xử lý & Áp dụng trọng số
    for i, doc in enumerate(documents):
        # Lấy nội dung, xử lý an toàn nếu trường đó không tồn tại
        title = (doc.get('title', '') + ' ') * 3  # Trọng số x3 cho tiêu đề
        category = (doc.get('category', '') + ' ') * 2 # Trọng số x2 cho thể loại
        area = (doc.get('area', '') + ' ') * 2 # Trọng số x2 cho khu vực
        
        # Ghép các thành phần trong 'ingredients' thành một chuỗi
        ingredients_list = doc.get('ingredients', [])
        ingredients = (', '.join(ingredients_list) + ' ') * 2 # Trọng số x2
        
        instructions = doc.get('instructions', '') # Trọng số x1 (mặc định)

        # Kết hợp tất cả thành một văn bản duy nhất để đưa vào TF-IDF
        combined_text = title + category + area + ingredients + instructions
        processed_docs.append(combined_text)
        
        # Lưu map ID
        doc_id_map[i] = doc['id']

    print(f"Đã xử lý và áp dụng trọng số cho {len(processed_docs)} tài liệu.")

    # 3. Build chỉ mục TF-IDF
    # TfidfVectorizer sẽ tự động:
    # - Chuyển chữ thường (lowercase=True)
    # - Tách từ (tokenization)
    # - Bỏ từ dừng tiếng Anh (stop_words='english')
    # - Loại bỏ dấu câu
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    
    tfidf_matrix = vectorizer.fit_transform(processed_docs)

    print(f"Kích thước ma trận TF-IDF: {tfidf_matrix.shape}")

    # 4. Lưu chỉ mục ra file
    joblib.dump(vectorizer, VECTORIZER_FILE)
    joblib.dump(tfidf_matrix, MATRIX_FILE)
    
    # Lưu lại list documents gốc và map ID để Module 3 có thể truy xuất
    # Chúng ta sẽ lưu 1 dict {id: doc} để truy cập nhanh
    documents_dict = {doc['id']: doc for doc in documents}
    joblib.dump(documents_dict, DOCUMENTS_FILE)
    
    joblib.dump(doc_id_map, os.path.join(DATA_DIR, 'doc_id_map.joblib'))

    print(f"--- ĐÃ XONG Module 2 ---")
    print(f"Đã lưu các file chỉ mục vào thư mục '{DATA_DIR}'.")

if __name__ == "__main__":
    run_indexing()