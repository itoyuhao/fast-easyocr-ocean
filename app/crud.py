from sqlalchemy.orm import Session
import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_name(db: Session, name: str):
    return db.query(models.User).filter(models.User.name == name).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(name=user.name, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_card(db: Session, owner_id: int):
    return db.query(models.Card).filter(models.Card.owner_id == owner_id).first()


def get_cards(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Card).offset(skip).limit(limit).all()


def create_user_card(db: Session, user_id: int, title: str, description: str=None, card_byte=None):
    db_card = models.Card(title=title, description=description, owner_id=user_id, card_byte=card_byte)
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card


def delete_user_card(db: Session, user_id: int):
    db_card = db.query(models.Card).filter_by(owner_id=user_id).first()
    if db_card:
        db.delete(db_card)
        db.commit()
        # db.refresh(db_card)
        return db_card
    else:
        return {'Card(s) not found': 'No cards.'}