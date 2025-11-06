from typing import List
from fastapi import APIRouter, HTTPException

import joblib
from src.app_config import app_config  
from src.schemas.recipe_schemas import SearchRequest, SearchResult
from src.search.engine import SearchEngine

router = APIRouter(tags=["search"])
search_engine = SearchEngine()


@router.post("/search", response_model=List[SearchResult])
def search_recipes(request: SearchRequest):
    """
    Tìm kiếm công thức nấu ăn dựa trên query với các bộ lọc tùy chọn
    """
    try:
        results = search_engine.search_recipes(request.query, request.top_k)
        if request.ingredients:
            # Tải dữ liệu đầy đủ để kiểm tra nguyên liệu
            try:
                documents_dict = joblib.load(app_config.DOCUMENTS_FILE_PATH)
                filtered_results = []
                for result in results:
                    recipe_data = documents_dict.get(result.id, {})
                    recipe_ingredients = recipe_data.get("ingredients", [])
                    # Kiểm tra xem có nguyên liệu nào được yêu cầu trong công thức không
                    if any(ingredient.lower() in " ".join(recipe_ingredients).lower()
                           for ingredient in request.ingredients):
                        filtered_results.append(result)

                results = filtered_results
            except Exception as e:
                print(f"Lỗi khi lọc nguyên liệu: {e}")
        return results
    
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy file index. Vui lòng chạy indexing trước."
        )
    except Exception as e:
        print(f"Lỗi search: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi tìm kiếm: {str(e)}"
        )
