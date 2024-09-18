from pydantic import BaseModel

class Favorite(BaseModel):
    username: str
    products: list