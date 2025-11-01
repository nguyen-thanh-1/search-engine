from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import json

from src.app_config import app_config
from src.schemas.recipe_schemas import Recipe, SearchResult
from src.search.engine import SearchEngine

router = APIRouter(prefix="/api", tags=["recipes"])
search_engine = SearchEngine()


@router.get("/recipes", response_model=List[Recipe])
def get_all_recipes(
    limit: Optional[int] = Query(None, description="Limit number of results"),
    category: Optional[str] = Query(None, description="Filter by category"),
    area: Optional[str] = Query(None, description="Filter by area")
):
    """
    Get all recipes with optional filtering
    """
    try:
        # Load documents from joblib file
        import joblib
        documents_dict = joblib.load(app_config.DOCUMENTS_FILE)

        recipes = []
        for recipe_id, recipe_data in documents_dict.items():
            # Apply filters if provided
            if category and recipe_data.get("category") != category:
                continue
            if area and recipe_data.get("area") != area:
                continue

            recipe = Recipe(
                id=recipe_id,
                title=recipe_data.get("title", ""),
                category=recipe_data.get("category"),
                area=recipe_data.get("area"),
                instructions=recipe_data.get("instructions"),
                image=recipe_data.get("image", ""),
                ingredients=recipe_data.get("ingredients", [])
            )
            recipes.append(recipe)

        # Apply limit if provided
        if limit:
            recipes = recipes[:limit]

        return recipes

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Recipe data not found. Please run indexing first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading recipes: {str(e)}")


@router.get("/recipes/{recipe_id}", response_model=Recipe)
def get_recipe_detail(recipe_id: str):
    """
    Get detailed information for a specific recipe
    """
    try:
        import joblib
        documents_dict = joblib.load(app_config.DOCUMENTS_FILE)

        if recipe_id not in documents_dict:
            raise HTTPException(status_code=404, detail="Recipe not found")

        recipe_data = documents_dict[recipe_id]

        recipe = Recipe(
            id=recipe_id,
            title=recipe_data.get("title", ""),
            category=recipe_data.get("category"),
            area=recipe_data.get("area"),
            instructions=recipe_data.get("instructions"),
            image=recipe_data.get("image", ""),
            ingredients=recipe_data.get("ingredients", [])
        )

        return recipe

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Recipe data not found. Please run indexing first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading recipe: {str(e)}")


@router.get("/categories", response_model=List[str])
def get_categories():
    """
    Get all available recipe categories
    """
    try:
        import joblib
        documents_dict = joblib.load(app_config.DOCUMENTS_FILE)

        categories = set()
        for recipe_data in documents_dict.values():
            category = recipe_data.get("category")
            if category and category != "N/A":
                categories.add(category)

        return sorted(list(categories))

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Recipe data not found. Please run indexing first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading categories: {str(e)}")


@router.get("/areas", response_model=List[str])
def get_areas():
    """
    Get all available cuisine areas
    """
    try:
        import joblib
        documents_dict = joblib.load(app_config.DOCUMENTS_FILE)

        areas = set()
        for recipe_data in documents_dict.values():
            area = recipe_data.get("area")
            if area and area != "N/A":
                areas.add(area)

        return sorted(list(areas))

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Recipe data not found. Please run indexing first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading areas: {str(e)}")


@router.get("/popular", response_model=List[SearchResult])
def get_popular_recipes(limit: int = Query(10, description="Number of popular recipes to return")):
    """
    Get popular recipes (simplified - returns first recipes)
    """
    try:
        import joblib
        documents_dict = joblib.load(app_config.DOCUMENTS_FILE)

        popular_recipes = []
        count = 0

        for recipe_id, recipe_data in documents_dict.items():
            if count >= limit:
                break

            recipe = SearchResult(
                id=recipe_id,
                title=recipe_data.get("title", ""),
                score=1.0,  # Default score for popular recipes
                category=recipe_data.get("category", "N/A"),
                area=recipe_data.get("area", "N/A"),
                image=recipe_data.get("image", "")
            )
            popular_recipes.append(recipe)
            count += 1

        return popular_recipes

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Recipe data not found. Please run indexing first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading popular recipes: {str(e)}")