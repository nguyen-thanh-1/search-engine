from typing import List
from fastapi import APIRouter, HTTPException, Query

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
            try:
                documents_dict = joblib.load(app_config.DOCUMENTS_FILE_PATH)
                filtered_results = []
                for result in results:
                    recipe_data = documents_dict.get(result.id, {})
                    recipe_ingredients = recipe_data.get("ingredients", [])
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


@router.get("/search/ingredients", response_model=List[SearchResult])
def search_by_ingredients(ingredients: str = Query(...), top_k: int = Query(10)):
    """
    Tìm kiếm công thức theo nguyên liệu (cách nhau bởi dấu phẩy)
    """
    try:
        ingredient_list = [ing.strip() for ing in ingredients.split(",") if ing.strip()]
        if not ingredient_list:
            raise HTTPException(
                status_code=400,
                detail="Vui lòng cung cấp ít nhất một nguyên liệu"
            )
        
        results = search_engine.search_by_ingredients(ingredient_list, top_k)
        return results
    
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy file index. Vui lòng chạy indexing trước."
        )
    except Exception as e:
        print(f"Lỗi search theo nguyên liệu: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi tìm kiếm: {str(e)}"
        )
