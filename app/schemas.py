from typing import List, Union
from pydantic import BaseModel


class CardBase(BaseModel):
    title: str
    description: Union[str, None] = None

class CardCreate(CardBase):
    pass


class Card(CardBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    name: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    cards: List[Card] = []

    class Config:
        orm_mode = True

