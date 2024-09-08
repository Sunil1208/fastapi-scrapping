class Notification:
    def notify(self, total_scraped: int, updated_count: int):
        print(f"Scraped {total_scraped} products. Updated {updated_count} products.")
