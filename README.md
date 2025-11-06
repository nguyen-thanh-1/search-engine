
## Cài đặt

### Backend

1. Di chuyển vào thư mục backend
```bash
cd backend
```

2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

3. Thiết lập file .env (đã có sẵn)
```bash
cat .env
```

Các biến cần thiết:
- `JSON_FILE_PATH`: Đường dẫn file JSON chứa dữ liệu công thức
- `VECTORIZER_FILE_PATH`: Đường dẫn lưu vectorizer
- `MATRIX_FILE_PATH`: Đường dẫn lưu TF-IDF matrix
- `DOCUMENTS_FILE_PATH`: Đường dẫn lưu dữ liệu documents
- `DOC_ID_MAP_FILE_PATH`: Đường dẫn lưu doc_id_map

### Frontend

1. Di chuyển vào thư mục frontend
```bash
cd frontend
```

2. Cài đặt dependencies
```bash
npm install
```

## Chạy ứng dụng

### Chạy Backend

Từ thư mục backend:
```bash
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Backend sẽ chạy tại: http://localhost:8000

API endpoints:
- `GET /` - Health check
- `POST /recipes` - Lấy danh sách công thức
- `GET /recipes/{id}` - Lấy chi tiết công thức
- `POST /search` - Tìm kiếm công thức
- `POST /crawl` - Crawl dữ liệu từ TheMealDB
- `POST /index` - Build TF-IDF index

### Chạy Frontend

Từ thư mục frontend:
```bash
npm start
```

Frontend sẽ chạy tại: http://localhost:5173

## Quy trình sử dụng

### 1. Crawl dữ liệu (lần đầu)

Gọi endpoint crawl:
```bash
curl -X POST http://localhost:8000/crawl \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["chicken", "beef", "pasta"],
    "categories": [],
    "delay": 1
  }'
```

Dữ liệu sẽ được lưu vào `data/recipes_by_keywords.json`

### 2. Build index

Gọi endpoint index:
```bash
curl -X POST http://localhost:8000/index
```

Quá trình:
1. Đọc file JSON
2. Xử lý documents và áp dụng trọng số
3. Build TF-IDF index
4. Lưu vectorizer, matrix, documents vào thư mục models/

### 3. Tìm kiếm

Frontend gọi endpoint search:
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "chicken",
    "top_k": 10
  }'
```

Trả về danh sách công thức được xếp hạng theo TF-IDF similarity score.

## Cấu trúc dự án

```
backend/
  src/
    app_config.py          - Cấu hình ứng dụng
    main.py               - Main FastAPI app
    crawling/
      crawler.py          - Crawl dữ liệu từ TheMealDB
    indexing/
      indexer.py          - Build TF-IDF index
    search/
      engine.py           - Search engine sử dụng TF-IDF
    routes/
      crawling_routes.py  - Routes cho crawl & index
      search_routes.py    - Routes cho search
      recipes_routes.py   - Routes cho recipes CRUD
    schemas/
      crawler_schemas.py  - Schema cho crawler requests
      recipe_schemas.py   - Schema cho recipe responses
  models/
    vectorizer.joblib     - Lưu vectorizer
    tfidf_matrix.joblib   - Lưu TF-IDF matrix
    documents.joblib      - Lưu dữ liệu documents
    doc_id_map.joblib     - Lưu mapping document index → recipe ID
  data/
    recipes_by_keywords.json - File JSON chứa dữ liệu crawl

frontend/
  index.html              - Trang chủ
  recipe.html             - Trang chi tiết công thức
  about.html              - Trang giới thiệu
  contact.html            - Trang liên hệ
  src/
    app.js                - Main app logic
    api-service.js        - API service
    recipe-detail.js      - Recipe detail page logic
  styles/
    main.css              - Main styles
    recipe-detail.css     - Recipe detail styles
```

## API Endpoints

### Search

**POST** `/search`
- Request: `{"query": "string", "top_k": int}`
- Response: `[{"id": "string", "title": "string", "score": float, ...}]`

### Recipes

**GET** `/recipes`
- Response: `[{recipe object}]`

**GET** `/recipes/{id}`
- Response: `{recipe object}`

**GET** `/categories`
- Response: `["string"]`

**GET** `/areas`
- Response: `["string"]`

**GET** `/popular`
- Response: `[{recipe object}]`

### Crawling & Indexing

**POST** `/crawl`
- Request: `{"keywords": [string], "categories": [string], "delay": int}`
- Response: `{"message": "string"}`

**POST** `/index`
- Response: `{"message": "string"}`

## Ghi chú

- Đảm bảo backend đang chạy trước khi mở frontend
- File `.env` phải được thiết lập đúng các đường dẫn
- Models phải được build từ endpoint `/index` trước khi search
- Frontend sử dụng API tại `http://localhost:8000`
