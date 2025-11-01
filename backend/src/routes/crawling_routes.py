from fastapi import APIRouter, BackgroundTasks, HTTPException

from src.crawling import TheMealDBCrawler
from src.indexing import run_indexing
from src.schemas.crawler_schemas import CrawlRequest

router = APIRouter(prefix="/api/crawl", tags=["crawling"])


@router.post("/start")
async def start_crawling(request: CrawlRequest, background_tasks: BackgroundTasks):
    """
    Start crawling data from TheMealDB API
    """

    def crawl_task():
        crawler = TheMealDBCrawler(delay=request.delay)
        if request.keywords:
            crawler.run_by_keywords(request.keywords)
        if request.categories:
            crawler.run_by_categories(request.categories)

    background_tasks.add_task(crawl_task)
    return {"message": "Crawling started in background"}


@router.post("/index")
def build_index():
    """
    Build TF-IDF search index from crawled data
    """
    try:
        run_indexing()
        return {"message": "Index built successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
