from pydantic import BaseModel

class ProductDetail(BaseModel):
    product_id: str
    product_name: str
    product_price: str
    product_image: str

class Product(BaseModel):
    product_id: str
    product_name: str
    product_price: str
    product_img: str
    quantity: int