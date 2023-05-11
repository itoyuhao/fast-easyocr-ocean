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

    cards = relationship("Card", back_populates="owner")

class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    card_byte = Column(LargeBinary)
    created_date = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="cards")