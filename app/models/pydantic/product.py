from pydantic import BaseModel, Field
from typing import Optional


class ProductModel(BaseModel):
    product_title: str = Field(..., title="Product Title", max_length=255)
    product_price: float = Field(..., gt=0, title="Product Price")
    path_to_image: Optional[str] = Field(None, title="Path to Image")

    class Config:
        schema_extra = {
            "example": {
                "product_title": "Example Product",
                "product_price": 199.99,
                "path_to_image": "/images/product1.jpg",
            }
        }
