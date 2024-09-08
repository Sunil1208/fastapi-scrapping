import redis


class CacheClient:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.client = redis.StrictRedis(
            host=host, port=port, db=db, decode_responses=True
        )

    def get_cached_price(self, product_title: str):
        cached_price = self.client.get(product_title)
        if cached_price is not None:
            try:
                return float(cached_price)
            except ValueError:
                return None
        return None

    def cache_price(self, product_title: str, product_price: float):
        self.client.set(product_title, product_price)
