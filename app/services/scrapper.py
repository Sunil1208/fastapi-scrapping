import os
import time

import requests
from bs4 import BeautifulSoup

from app.models.pydantic.product import ProductModel


class Scrapper:
    def __init__(self, base_url, proxy=None, max_retries=3, retry_delay=10):
        self.base_url = base_url
        self.proxy = proxy
        self.max_retries = max_retries
        self.retry_delay = retry_delay  # time to wait before retrying
        self.image_dir = "images"
        os.makedirs(self.image_dir, exist_ok=True)  # Ensure image directory exists

    def scrape_page(self, page_num):
        url = f"{self.base_url}/page/{page_num}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        attempts = 0
        while attempts < self.max_retries:
            try:
                if self.proxy:
                    response = requests.get(
                        url,
                        headers=headers,
                        proxies={"http": self.proxy, "https": self.proxy},
                    )
                else:
                    response = requests.get(url, headers=headers)

                # If the request was successful, break the retry loop
                response.raise_for_status()  # This will raise an error for bad responses
                break

            except requests.exceptions.RequestException as e:
                attempts += 1
                print(f"Error scraping page {page_num}, attempt {attempts}: {e}")

                if attempts < self.max_retries:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)  # Wait before retrying
                else:
                    raise Exception(
                        f"Failed to scrape page {page_num} after {self.max_retries} attempts: {e}"
                    )

        soup = BeautifulSoup(response.content, "html.parser")
        products = []

        for product_item in soup.select(".products"):
            title_elem = product_item.select_one("h2.woo-loop-product__title a")
            price_elem = product_item.select_one("span.price ins span.amount")
            img_elem = product_item.select_one("div.mf-product-thumbnail img")

            if not (title_elem and price_elem and img_elem):
                continue  # Skip this product if any of the elements are missing

            product_title = title_elem.text.strip()
            price_text = price_elem.text.strip().replace("₹", "").replace(",", "")

            try:
                product_price = float(price_text)
            except ValueError:
                continue  # Skip this product if the price is not a valid float

            image_url = img_elem.get("data-lazy-src") or img_elem.get("src")
            # Skip if image is a data URL (e.g., SVG placeholder)
            if image_url.startswith("data:"):
                print(f"Skipping placeholder image for {product_title}")
                continue

            image_filename = os.path.join(self.image_dir, os.path.basename(image_url))

            # Download and save the image
            try:
                img_data = requests.get(image_url).content
                with open(image_filename, "wb") as img_file:
                    img_file.write(img_data)
            except Exception as e:
                print(f"Error downloading image for {product_title}: {e}")
                continue

            product = ProductModel(
                product_title=product_title,
                product_price=product_price,
                path_to_image=image_filename,
            )

            products.append(product)
        return products
