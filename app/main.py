from fastapi import FastAPI, Query, Request

from app.auth.auth import authenticator
from app.config import BASE_URL

# from app.models.pydantic.product import ProductModel
from app.services.cache import CacheClient
from app.services.database import DatabaseClient
from app.services.notification import Notification
from app.services.scrapper import Scrapper

# Initialize the FastAPI app
app = FastAPI()


# Scrapping service to handle the logic
class ScrappingService:
    def __init__(self, scraper, db_client, cache_client, notifier):
        self.scraper = scraper
        self.db_client = db_client
        self.cache_client = cache_client
        self.notifier = notifier

    def run_scraping(self, page_limit):
        all_products = []
        for page_num in range(1, page_limit + 1):
            try:
                products = self.scraper.scrape_page(page_num)
                all_products.extend(products)
            except Exception as e:
                print(f"Error scrapping page {page_num}: {e}")
                continue
        self._process_scraped_data(all_products)

    def _process_scraped_data(self, products):
        updated_count = 0
        existing_data = self.db_client.load_data()

        for product in products:
            cached_price = self.cache_client.get_cached_price(product.product_title)

            # If cached price is the same, skip the update
            if cached_price is not None and cached_price == product.product_title:
                continue

            # Cache the new price and update the database
            self.cache_client.cache_price(product.product_title, product.product_title)

            existing_data.append(product)
            updated_count += 1

        self.db_client.save_data(existing_data)
        self.notifier.notify(len(products), updated_count)


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
    scrapping_service.run_scraping(limit)

    return {"message": "Scraping completed successfully!"}
