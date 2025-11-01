import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.app_config import app_config
from src.routes.crawling_routes import router as crawling_router
from src.routes.search_routes import router as search_router
from src.routes.recipes_routes import router as recipes_router

app = FastAPI(
    title="Recipe Search API",
    description="API for searching recipes using TF-IDF vectorization",
    debug=app_config.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    return {"message": "Recipe Search API is running"}


app.include_router(recipes_router)
app.include_router(search_router)
app.include_router(crawling_router)


if __name__ == "__main__":
    uvicorn.run(app, host=app_config.api_host, port=app_config.api_port)
