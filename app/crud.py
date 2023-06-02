from sqlalchemy.orm import Session
import models, schemas

# user-related
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


# file-related
def get_file(db: Session, owner_id: int):
    return db.query(models.File).filter(models.File.owner_id == owner_id).first()


def get_file_by_user_name_file_title(db: Session, user_name:str, file_title: str):
    user = db.query(models.User).filter(models.User.name == user_name).first()
    return db.query(models.File).filter(models.File.title == file_title, models.File.owner_id == user.id).first()


def get_files(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.File).offset(skip).limit(limit).all()


def create_user_file(db: Session, user_id: int, title: str, description: str=None, file_path=None):
    db_file = models.File(title=title, description=description, owner_id=user_id, file_path=file_path)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


def delete_user_file(db: Session, user_id: int):
    db_file =  db.query(models.File).filter_by(owner_id=user_id).delete()
    if db_file:
        db.commit()
        return {'Result': 'File(s) deleted'}
    else:
        return {'File not found': 'No such file.'}
    

# model-related
def get_model(db: Session, model_name: str):
    return db.query(models.Model).filter(models.Model.model_name == model_name).first()


def create_model(db: Session, model: schemas.ModelCreate):
    # model_path = "/models/" + model.model_name
    db_model = models.Model(model_name=model.model_name, description=model.description, model_path=model.model_path)
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


# prompt-related
def get_prompt(db: Session, prompt_title: str):
    return db.query(models.Prompt).filter(models.Prompt.prompt_title == prompt_title).first()


def get_prompt_content(db: Session, prompt_title: str):
    db_prompt = db.query(models.Prompt).filter(models.Prompt.prompt_title == prompt_title).first()
    with open(db_prompt.prompt_path, 'rb') as file:
        return file.read()


def create_prompt(db: Session, prompt_title: str, prompt_desc: str):
    prompt_path = "prompts/" + prompt_title + ".txt"
    db_prompt = models.Prompt(prompt_title=prompt_title, prompt=prompt_desc, prompt_path=prompt_path)
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt


def update_prompt_title(db: Session, prompt_title: str, new_prompt_title: str):
    db_prompt = get_prompt(db=db, prompt_title=prompt_title)
    db_prompt.prompt_title = new_prompt_title
    new_prompt_path = "prompts/" + db_prompt.prompt_title + ".txt"
    db_prompt.prompt_path = new_prompt_path
    db.commit()
    db.refresh(db_prompt)
    return db_prompt


# page-related
def get_page(db: Session, page_title: str, file_id: int, user_name: str):
    # db_page = db.query(models.Page).filter(models.Page.page_title == page_title).all()
    # db_user = db.query(models.User).filter(models.User.name == user_name).first()
    # db_file = db.query(models.File).filter(models.File.owner_id == db_user.id, models.File.title == ).
    return db.query(models.Page).filter(models.Page.page_title == page_title, models.Page.file_id == file_id).first()


def save_page(db: Session, page_title: str, file_used: str, model_used: str="default", prompt_used: str="default"):

    # get file id
    db_file = db.query(models.File).filter(models.File.title == file_used).first()
    # create object for load in
    db_page = models.Page(page_title=page_title, html_path="pages/"+page_title+".html", file_id=db_file.id, model_used=model_used, prompt_used=prompt_used)
    db.add(db_page)
    db.commit()
    db.refresh(db_page)
    return db_page