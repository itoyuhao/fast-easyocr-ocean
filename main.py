from fastapi import FastAPI, UploadFile
from typing import Optional, Union
from pydantic import BaseModel
import io
import uvicorn
import easyocr

app = FastAPI()
ocr_reader = easyocr.Reader(['en', 'ch_tra'])

@app.get("/")
async def read_root():
    return {"Hello": "Hello from FastAPI"}

@app.post("/easyocr")
async def ocr_model(file: Union[UploadFile, None] = None):
    if not file:
        return {"message": "No upload file sent."}
    else:
        image_bytes = io.BytesIO(file.file.read()).read()
        result = ocr_reader.readtext(image_bytes)
        return {"saved_filename": file.filename, "result": str(result)}


if __name__ == "__main__":
    uvicorn.run(app, port=8000)