from fastapi import FastAPI, Query, Request

from app.auth.auth import authenticator
from app.config import BASE_URL

# from app.models.pydantic.product import ProductModel
from app.services.cache import CacheClient
from app.services.database import DatabaseClient
from app.services.notification import Notification
from app.services.scraping_service import ScrappingService
from app.services.scrapper import Scrapper

# Initialize the FastAPI app
app = FastAPI()


# FastAPI route to trigger the scrapping process
@app.get("/scrape")
@authenticator()
async def scrape(
    request: Request,
    limit: int = 5,
    proxy: str = "",
    max_retries: int = Query(3, ge=1),
    retry_delay: int = Query(5, ge=1),
):
    scraper = Scrapper(
        base_url=BASE_URL, proxy=proxy, max_retries=max_retries, retry_delay=retry_delay
    )
    db_client = DatabaseClient()
    cache_client = CacheClient()
    notifier = Notification()

    # Initialize and run the scraping service
    scrapping_service = ScrappingService(scraper, db_client, cache_client, notifier)
    scrapping_service.run_scraping(page_limit=limit)

    return {"message": "Scraping completed successfully!"}
