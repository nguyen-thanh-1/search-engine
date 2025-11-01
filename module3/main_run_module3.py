# main.py

import os
from module3 import SearchEngine
from module2 import run_indexing

# Đường dẫn kiểm tra
DATA_DIR = 'data'
VECTORIZER_FILE = os.path.join(DATA_DIR, 'vectorizer.joblib')

def run_tests(engine):
    """Chạy một vài truy vấn mẫu để kiểm tra."""
    print("\n--- CHẠY THỬ NGHIỆM ---")

    test_queries = [
        "spicy chicken",
        "beef with potatoes and carrots",
        "japanese rice",
        "french chicken"
    ]

    for query in test_queries:
        print(f"\n[?] Đang tìm kiếm cho: '{query}'")
        results = engine.search(query, top_k=5)
        if not results:
            print("Không tìm thấy kết quả nào.")
        else:
            for res in results:
                print(f"  -> [Score: {res['score']:.4f}] {res['title']} ({res['area']})")

def start_interactive_search(engine):
    """Cho phép người dùng tự gõ truy vấn."""
    print("\n--- TÌM KIẾM TƯƠNG TÁC ---")
    print("Gõ truy vấn của bạn và nhấn Enter. Gõ 'exit' để thoát.")
    
    while True:
        try:
            query = input("\nNhập truy vấn > ")
            if query.lower() == 'exit':
                break
            
            results = engine.search(query, top_k=5)
            
            if not results:
                print("Không tìm thấy kết quả nào phù hợp.")
            else:
                print(f"--- {len(results)} kết quả hàng đầu ---")
                for res in results:
                    print(f"  [Score: {res['score']:.4f}] {res['title']} (ID: {res['id']})")
                    print(f"    -> Thể loại: {res['category']} | Khu vực: {res['area']}")
                    # print(f"   -> Ảnh: {res['image']}") # Bỏ comment nếu muốn xem link ảnh
        
        except KeyboardInterrupt:
            print("\nĐã thoát.")
            break

if __name__ == "__main__":
    # 1. KIỂM TRA & BUILD CHỈ MỤC (MODULE 2)
    # Kiểm tra xem file chỉ mục đã tồn tại chưa
    if not os.path.exists(VECTORIZER_FILE):
        print(f"Không tìm thấy chỉ mục trong '{DATA_DIR}'.")
        print("Đang tự động chạy 'build_index.py' (Module 2)...")
        run_indexing()
    else:
        print(f"Đã tìm thấy chỉ mục, bỏ qua bước build (Module 2).")

    # 2. KHỞI TẠO BỘ MÁY TÌM KIẾM (MODULE 3)
    engine = SearchEngine()

    # 3. CHẠY THỬ
    run_tests(engine)
    
    # 4. CHẠY TƯƠNG TÁC
    start_interactive_search(engine)