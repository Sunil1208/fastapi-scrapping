import json
import os
from app.models.pydantic.product import ProductModel


class DatabaseClient:
    def __init__(self, file_path="scrapped_data.json"):
        self.file_path = file_path
        if not os.path.exists(self.file_path):
            self._initialize_db()

        def _initialize_db(self):
            with open(self.file_path, "w") as db_file:
                json.dump([], db_file)

        def load_data(self):
            with open(self.file_path, "r") as db_file:
                data = json.load(db_file)
                return [ProductModel(**item) for item in data]

        def save_data(self, data):
            with open(self.file_path, "w") as f:
                json.dump([item.dict() for item in data], f, indent=4)
