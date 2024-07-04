import uuid
from typing import Union

from pydantic import BaseModel


class ItemResponse(BaseModel):
    id: Union[str, uuid.UUID]
    name: str
    description: str
    price: float
    quantity: int
    user_id: Union[str, uuid.UUID]


class UserCreate(BaseModel):
    username: str


class UserResponse(UserCreate):
    id: Union[str, uuid.UUID]


class DatabaseRequest(BaseModel):
    user_count: int = 500
    item_count: int = 20000
