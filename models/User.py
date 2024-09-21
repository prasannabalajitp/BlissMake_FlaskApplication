from pydantic import BaseModel

class User(BaseModel):
    username: str
    email: str
    address: str
    phone: str