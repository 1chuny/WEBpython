from pydantic import BaseModel
from typing import List, Optional

class DishBase(BaseModel):
    name: str
    price: float

class DishCreate(DishBase):
    pass

class Dish(DishBase):
    id: int
    class Config:
        from_attributes = True # Дозволяє працювати з об'єктами SQLAlchemy

class UserBase(BaseModel):
    username: str
    role: str

class OrderBase(BaseModel):
    user_id: int
    dish_id: int
    status: str