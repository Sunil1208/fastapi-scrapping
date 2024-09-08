from typing import Optional

from pydantic import BaseModel, Field


class ProductModel(BaseModel):
    product_title: str = Field(..., title="Product Title", max_length=255)
    product_price: float = Field(..., gt=0, title="Product Price")
    path_to_image: Optional[str] = Field(None, title="Path to Image")
