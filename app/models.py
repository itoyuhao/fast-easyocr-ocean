from sqlalchemy import  Column, ForeignKey
from sqlalchemy import Boolean, Integer, String, LargeBinary, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime(timezone=True), default=func.now())

    files = relationship("File", back_populates="owner")


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    file_path = Column(String, unique=True, index=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="files")
    pages = relationship("Page", back_populates="file")

class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    page_title = Column(String, index=True)
    html_path = Column(String, index=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    model_used = Column(Integer, ForeignKey("models.id"))
    prompt_used = Column(Integer, ForeignKey("prompts.id"))
    created_date = Column(DateTime(timezone=True), default=func.now())

    file = relationship("File", back_populates="pages")
    model = relationship("Model", back_populates="pages")
    prompt = relationship("Prompt", back_populates="pages")

class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, unique=True, index=True)
    description = Column(String)
    model_path = Column(String, index=True)
    created_date = Column(DateTime(timezone=True), default=func.now())

    pages = relationship("Page", back_populates="model")

class Prompt(Base):
    __tablename__ = "prompts"
    id = Column(Integer, primary_key=True, index=True)
    prompt_title = Column(String, unique=True, index=True)
    prompt = Column(String)
    prompt_path = Column(String, default="/prompts/default.txt")
    created_date = Column(DateTime(timezone=True), default=func.now())

    pages = relationship("Page", back_populates="prompt")