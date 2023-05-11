import os, sys

from typing import Union, List

from fastapi import Depends, FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

import io
import uvicorn
import easyocr
import codecs

import crud, models, schemas
from database import SessionLocal, engine

REPO_DIR = os.path.dirname(os.getcwd())
sys.path.append(REPO_DIR)

from utils.timer import timed


models.Base.metadata.create_all(bind=engine)

app = FastAPI()
ocr_reader = easyocr.Reader(['en', 'ch_tra'])

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 

# welcome page(root)
@timed
@app.get("/")
async def read_root():
    return {"Hello": "Hello from FastAPI"}


# database-related api
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, name=user.name)
    if db_user:
        raise HTTPException(status_code=400, detail="Name already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/cards/", response_model=schemas.Card)
def create_card_for_user(
    user_id: int, 
    # card: schemas.CardCreate, 
    title: str = None,
    description: str = None,
    files: Union[UploadFile, None] = None, 
    db: Session = Depends(get_db)
):
    if files:
        file_byte = io.BytesIO(files.file.read()).read()
    else:
        file_byte = None
    return crud.create_user_card(db=db, 
                                 title=title, 
                                 description=description, 
                                 user_id=user_id, 
                                 card_byte=file_byte)


@app.get("/cards/", response_model=List[schemas.Card])
def read_cards(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cards = crud.get_cards(db, skip=skip, limit=limit)
    return cards


@app.delete("/cards/{user_id}/delete/")
def delete_all_cards(user_id: int, db: Session = Depends(get_db)):
    cards = crud.delete_user_card(db, user_id=user_id)
    return cards


# ocr-related api
@app.post("/easyocr")
async def ocr_model(db: Session = Depends(get_db), files: Union[UploadFile, None] = None):
    if not files:
        return {"message": "No upload file sent."}
    else:
        image_bytes = io.BytesIO(files.file.read()).read()
        crud.create_user_card(db=db, 
                                 title='upload_card', 
                                 description='upload_for_ocr', 
                                 user_id=1, 
                                 card_byte=image_bytes)
        result = ocr_reader.readtext(image_bytes)
        return {"saved_filename": files.filename, "result": str(result)}


@app.get("/upload")
async def main():
    html = codecs.open("frontend/upload.html", "r").read()

    return HTMLResponse(content=html)


if __name__ == "__main__":
    uvicorn.run(app, port=8000)
