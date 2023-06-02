from typing import List, Union
from pydantic import BaseModel


# pages
class PageBase(BaseModel):
    page_title: str
    file_id: int
    model_used: int
    prompt_used: int


class PageCreate(PageBase):
    pass
    

class Page(PageBase):
    id: int
    file_id: int

    class Config:
        orm_mode = True


# files
class FileBase(BaseModel):
    title: str
    description: Union[str, None] = None


class FileCreate(FileBase):
    pass


class File(FileBase):
    id: int
    owner_id: int
    pages: List[Page] = []

    class Config:
        orm_mode = True


# users
class UserBase(BaseModel):
    name: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    files: List[File] = []

    class Config:
        orm_mode = True


# models
class ModelBase(BaseModel):
    model_name: str
    description: Union[str, None] = None
    model_path: str


class ModelCreate(ModelBase):
    pass


class Model(ModelBase):
    id: int
    pages: List[Page] = []

    class Config:
        orm_mode = True


# prompts
class PromptBase(BaseModel):
    prompt_title: str
    prompt: str


class PromptCreate(PromptBase):
    pass


class Prompt(PromptBase):
    id: int
    prompt_path: str
    pages: List[Page] = []

    class Config:
        orm_mode = True