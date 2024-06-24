from pydantic import BaseModel
# import union and uuid
from typing import Union
import uuid

class Item(BaseModel):
    id: Union[str, uuid.UUID]
    name: str
    description: str
    price: float
    quantity: int
    user_id: Union[str, uuid.UUID]

class User(BaseModel):
    id: Union[str, uuid.UUID]
    username: str

class UserCreate(BaseModel):
    username: str