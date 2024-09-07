import requests
from bs4 import BeautifulSoup
import os
from app.models.pydantic.product import ProductModel


class Scrapper:
    def __init__(self, base_url, proxy=None):
        self.base_url = base_url
        self.proxy = proxy

    def scrape_page(self, page_num):
        url = f"{self.base_url}/page/{page_num}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        try:
            if self.proxy:
                response = requests.get(
                    url,
                    headers=headers,
                    proxies={"http": self.proxy, "https": self.proxy},
                )
            else:
                response = requests.get(url, headers=headers)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error scrapping page {page_num}: {e}")

        soup = BeautifulSoup(response.content, "html.parser")
        products = []

        for product_item in soup.select(".product-item"):
            title_elem = product_item.select_one(".product-title")
            price_elem = product_item.select_one(".product-price")
            img_elem = product_item.select_one(".product-image img")

            if not (title_elem and price_elem and img_elem):
                continue  # Skip this product if any of the elements are missing

            product_title = title_elem.text.strip()
            price_text = price_elem.text.strip().replace("₹", "").replace(",", "")

            try:
                product_price = float(price_text)
            except ValueError:
                continue  # Skip this product if the price is not a valid float

            image_url = img_elem["src"]
            image_filename = os.path.basename("images", os.path.basename(image_url))

            # Download and save the image

            try:
                img_data = requests.get(image_url).content
                os.mkdir("images", exist_ok=True)
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
