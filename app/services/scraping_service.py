from typing import List, Optional

from app.models.pydantic.product import ProductModel
from app.services.cache import CacheClient
from app.services.database import DatabaseClient
from app.services.notification import Notification
from app.services.scrapper import Scrapper


class ScrappingService:
    def __init__(
        self,
        scraper: Scrapper,
        db_client: DatabaseClient,
        cache_client: CacheClient,
        notifier: Notification,
    ):
        self.scraper = scraper
        self.db_client = db_client
        self.cache_client = cache_client
        self.notifier = notifier

    def run_scraping(self, page_limit: int, return_scraped_data: bool = False):
        all_products: List[ProductModel] = []
        for page_num in range(1, page_limit + 1):
            try:
                products = self.scraper.scrape_page(page_num)
                all_products.extend(products)
            except Exception as e:
                print(f"Error scrapping page {page_num}: {e}")
                continue
        self._process_scraped_data(all_products)
        if return_scraped_data:
            return all_products
        return None

    def _process_scraped_data(self, products: List[ProductModel]):
        updated_count = 0
        existing_data: List[ProductModel] = self.db_client.load_data()

        for product in products:
            cached_price: Optional[float] = self.cache_client.get_cached_price(
                product.product_title
            )

            # If cached price is the same, skip the update
            if cached_price is not None and cached_price == product.product_price:
                continue

            # Cache the new price and update the database
            self.cache_client.cache_price(product.product_title, product.product_price)

            existing_data.append(product)
            updated_count += 1

        self.db_client.save_data(existing_data)
        self.notifier.notify(len(products), updated_count)

    def get_all_products(self) -> List[ProductModel]:
        existing_data: List[ProductModel] = self.db_client.load_data()
        return existing_data
