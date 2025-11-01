from typing import List

from fastapi import APIRouter

from src.app_config import app_config
from src.schemas.recipe_schemas import SearchRequest, SearchResult
from src.search.engine import SearchEngine

router = APIRouter(prefix="/api/search", tags=["search"])
search_engine = SearchEngine()


@router.post("/", response_model=List[SearchResult])
def search_recipes(request: SearchRequest):
    """
    Search for recipes based on query with optional filters
    """
    # Get basic search results
    results = search_engine.search_recipes(request.query, request.top_k)

    # Apply filters if provided
    if request.category:
        results = [r for r in results if r.category == request.category]

    if request.area:
        results = [r for r in results if r.area == request.area]

    # For ingredient filtering, we'd need to check the full recipe data
    # This is a simplified implementation
    if request.ingredients:
        # Load full documents to check ingredients
        try:
            import joblib
            documents_dict = joblib.load(app_config.DOCUMENTS_FILE)

            filtered_results = []
            for result in results:
                recipe_data = documents_dict.get(result.id, {})
                recipe_ingredients = recipe_data.get("ingredients", [])

                # Check if any requested ingredient is in the recipe
                if any(ing.lower() in " ".join(recipe_ingredients).lower()
                      for ing in request.ingredients):
                    filtered_results.append(result)

            results = filtered_results
        except Exception:
            # If filtering fails, return unfiltered results
            pass

    return results
