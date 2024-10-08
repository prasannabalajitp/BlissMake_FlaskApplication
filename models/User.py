from pydantic import BaseModel

class User(BaseModel):
    username: str
    email: str
    address: str
    phone: str

class UpdateAddres(BaseModel):
    address: str
    phone: str