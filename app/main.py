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
import aiofiles
import requests

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
    return {"Hello": "Hello there, welcome to the website. Please have a look."}


# database-related api
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/user/", response_model=schemas.User, tags=["users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, name=user.name)
    if db_user:
        raise HTTPException(status_code=400, detail="Name already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User], tags=["users"])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/user/{user_name}", response_model=schemas.User, tags=["users"])
def read_user(user_name: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, name=user_name)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/file/create", response_model=schemas.File, tags=["files"])
async def create_file_for_user(
    user_name: str, 
    title: str,
    description: str = None,
    files: Union[UploadFile, None] = None, 
    db: Session = Depends(get_db)
):
    db_user = crud.get_user_by_name(db, name=user_name)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if files:
        file_path = 'files/' + files.filename

        # 目前存檔後檔案會毀損, 待修復.
        async with aiofiles.open(file_path, 'wb') as out_file:
            while content := await files.read(1024):  # async read chunk
                await out_file.write(content)
        return crud.create_user_file(db=db, 
                                 title=title, 
                                 description=description, 
                                 user_id=db_user.id, 
                                 file_path=file_path)
    else:
        return {'Result': 'No file upload.'}
    

@app.get("/files/", response_model=List[schemas.File], tags=["files"])
def read_files(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    files = crud.get_files(db, skip=skip, limit=limit)
    return files


@app.get("/file/", tags=["files"])
def read_file(user_name: str, file_title: str, db: Session = Depends(get_db)):
    files = crud.get_file_by_user_name_file_title(db, user_name=user_name, file_title=file_title)
    if files is None:
        raise HTTPException(status_code=404, detail="User or file title not found")
    return files


@app.delete("/files/delete/", tags=["files"])
def delete_all_files(user_id: int, db: Session = Depends(get_db)):
    files = crud.delete_user_file(db, user_id=user_id)
    return files


@app.post("/model", tags=["models"])
def create_model(model: schemas.ModelCreate, db: Session = Depends(get_db)):
    db_model = crud.get_model(db, model_name=model.model_name)
    if db_model:
        raise HTTPException(status_code=400, detail="Model already registered")
    return crud.create_model(db=db, model=model)


@app.get("/model/{model_name}", response_model=schemas.Model, tags=["models"])
def read_model(model_name: str, db: Session = Depends(get_db)):
    db_model = crud.get_model(db, model_name=model_name)
    if db_model is None:
        raise HTTPException(status_code=404, detail="Model not found")
    return db_model


@app.post("/prompt/create", tags=["prompts"])
async def create_prompt(
    prompt_title: str,
    prompt_desc: str = None,
    file: Union[UploadFile, None] = None, 
    db: Session = Depends(get_db)):
    db_prompt = crud.get_prompt(db, prompt_title=prompt_title)
    if db_prompt:
        raise HTTPException(status_code=400, detail="Title of prompt already registered")

    async with aiofiles.open("prompts/"+prompt_title+".txt", 'wb') as out_file:
        while content := await file.read(1024):  # async read chunk
            await out_file.write(content)

    return crud.create_prompt(db=db, prompt_title=prompt_title, prompt_desc=prompt_desc)


@app.get("/prompt/{prompt_title}", tags=["prompts"])
def read_prompt_template(prompt_title: str, db: Session = Depends(get_db)):
    db_prompt = crud.get_prompt(db, prompt_title=prompt_title)
    if db_prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return db_prompt


@app.post("/prompt/rename", tags=["prompts"])
def rename_prompt(prompt_title: str, new_prompt_title: str, db: Session = Depends(get_db)):
    db_prompt = crud.get_prompt(db, prompt_title=prompt_title)
    if db_prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")
    else:
        return crud.update_prompt_title(db=db, prompt_title=prompt_title, new_prompt_title=new_prompt_title)


@app.get("/prompt/prompt_content/{prompt_used}", tags=["prompts"])
def generate_prompt_content(prompt_used: str, text:str = None, db: Session = Depends(get_db)):
    db_prompt = crud.get_prompt_content(db, prompt_title=prompt_used)
    if text:
        return db_prompt.decode("utf-8").format(text=text)
    return db_prompt.decode("utf-8").format(text='fill your content here')


# @app.post("/page/create", tags=["pages"])
# def create_page_for_user(page: schemas.PageCreate, db: Session = Depends(get_db)):
#     db_page = crud.get_page(db, page_title=page.page_title, file_id=page.file_id)
#     if db_page:
#         raise HTTPException(status_code=400, detail="Page for this title has been created. Please use another page title.")
#     return crud.create_page(db, page=page)


@app.get("/page/create", tags=["pages"])
async def create_page_for_user(user_name: str
                       , page_title: str
                       , file_used: str
                       , model_used: str="default"
                       , prompt_used: str="default"
                       , save: int=0
                       , db: Session = Depends(get_db)):
    
    # selet uploaded file
    db_file = crud.get_file_by_user_name_file_title(user_name=user_name, file_title=file_used, db=db)
    # select model: default -> easyocr model
    db_model = crud.get_model(model_name=model_used, db=db)

    # parse file and ask gpt.
    if (model_used == "default") and (prompt_used == 'default'):
        with open(db_file.file_path, 'rb') as image:
            b = io.BytesIO(image.read()).read()
            parsed = ocr_reader.readtext(b)
            text = ' '.join([x[1] for x in parsed])
            db_prompt = crud.get_prompt_content(db, prompt_title=prompt_used)
        
        gpt_response = requests.get(db_prompt.decode("utf-8").format(text=text))
        result = gpt_response.text
        # save file and data if needed
        if save:
            with open("pages/"+page_title+".html", 'w') as out_file:
                out_file.write(result)
            crud.save_page(db=db, page_title=page_title, file_used=file_used, model_used=model_used, prompt_used=prompt_used)
        return HTMLResponse(content=result)



@app.get("/page/{file_id}/{page_title}", tags=["pages"])
def read_page(file_id: int, page_title: str, db: Session = Depends(get_db)):
    db_page = crud.get_page(db, file_id=file_id, page_title=page_title)
    if db_page is None:
        raise HTTPException(status_code=404, detail="Page not found")
    return db_page


@app.get("/parse/file", tags=["others"])
async def parse_by_file_path(user_name: str, file_used: str, db: Session = Depends(get_db)):
    db_file = crud.get_file_by_user_name_file_title(user_name=user_name, file_title=file_used, db=db)
    if db_file:
        with open(db_file.file_path, 'rb') as image:
            b = io.BytesIO(image.read()).read()
            parsed = ocr_reader.readtext(b)
            text = ' '.join([x[1] for x in parsed])
            r_info = requests.get(f'''http://bio.ppl.ai/chat.php?text=你現在是一個文字專家，現在有一個任務，會給你一串文字，這些文字都是來自辨識名片的結果。
            你需要判斷這些文字所代表的意義，像是中文姓名、中文地址、英文地址、公司電話、個人手機號碼、職稱、公司名稱、
            英文名字、電子郵件、社群媒體帳號或 ID （也請個別列點）、統一編號、公司/個人業務內容等等，也就是名片上會有的各種資訊。
            不一定每一項資訊都會出現，要根據文字代表的意義去做分類。只需要回傳相關資訊即可。
            請用列點的方式告訴我，並以 「意義：文字」的格式回答我，
            任務開始：
            以下是要請你幫我判斷的文字訊息
            ```
            {text}
            ```''')

            info_list = r_info.text.split("- ")
            info_list = info_list[1:]
            info_list = [i.replace("\n","") for i in info_list]

            info_list_index = [i.split("：")[0] for i in info_list]
            info_list_value = [i.split("：")[1] for i in info_list]

            info_dict = dict(zip(info_list_index, info_list_value))

            response = requests.get(f'http://bio.ppl.ai/chat.php?text=我將提供一個含有個人的就職公司/職稱等資訊的python dictionary, 請你根據這個dictionary產出一個美觀、設計感、有色彩、含有動態元素的個人網站, 並轉為前端呈現的程式碼, 回傳純程式碼即可, 不要有任何非程式碼的文字:```{info_dict}```')
            result = response.text
        return HTMLResponse(content=result)
    raise HTTPException(status_code=400, detail="File not found")


@app.get("/parse/{user_id}", tags=["others"])
async def parse(user_id: int, db: Session = Depends(get_db)):
    result = crud.get_file(owner_id=user_id, db=db)
    if result:
        return {"result" : str(result)}
    raise HTTPException(status_code=400, detail="File not found")


# ocr-related api
@app.post("/easyocr", tags=["others"])
async def ocr_model(db: Session = Depends(get_db), files: Union[UploadFile, None] = None):
    if not files:
        return {"message": "No upload file sent."}
    else:
        # save file
        # out_to_path = files.filename
        
        image_bytes = io.BytesIO(files.file.read()).read()
        # crud.create_user_file(db=db, 
        #                          title='upload_file', 
        #                          description='upload_for_ocr', 
        #                          user_id=1, 
        #                          file_path= 'files/' + files.filename)
        result = ocr_reader.readtext(image_bytes)

        # async with aiofiles.open(out_to_path, 'wb') as out_file:
        #     while content := await files.read(1024):  # async read chunk
        #         await out_file.write(content)
        return {"saved_filename": files.filename, "result": str(result)}


@app.get("/upload", tags=["others"])
async def upload():
    html = codecs.open("frontend/upload.html", "r").read()

    return HTMLResponse(content=html)



if __name__ == "__main__":
    uvicorn.run(app, port=8000)
