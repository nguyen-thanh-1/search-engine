from fastapi import APIRouter, BackgroundTasks, HTTPException

from src.crawling.crawler import TheMealDBCrawler
from src.indexing.indexer import Indexer
from src.schemas.crawler_schemas import CrawlRequest

router = APIRouter(tags=["crawling"])


@router.post("/crawl")
async def start_crawling(request: CrawlRequest, background_tasks: BackgroundTasks):
    """
    Bắt đầu crawl dữ liệu từ TheMealDB API
    """

    def crawl_task():
        crawler = TheMealDBCrawler(delay=request.delay)
        if request.keywords:
            crawler.run_by_keywords(request.keywords)
        if request.categories:
            crawler.run_by_categories(request.categories)

    background_tasks.add_task(crawl_task)
    return {"message": "Đã bắt đầu crawl dữ liệu trong nền"}


@router.post("/index")
def build_index():
    """
    Xây dựng chỉ mục tìm kiếm TF-IDF từ dữ liệu đã crawl
    """
    try:
        indexer = Indexer()
        indexer.index_recipes()
        return {"message": "Xây dựng chỉ mục thành công"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
