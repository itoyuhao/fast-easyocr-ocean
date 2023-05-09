from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import Optional, Union
from pydantic import BaseModel
import io
import uvicorn
import easyocr

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


@app.get("/")
async def read_root():
    return {"Hello": "Hello from FastAPI"}


@app.post("/easyocr")
async def ocr_model(files: Union[UploadFile, None] = None):
    if not files:
        return {"message": "No upload file sent."}
    else:
        image_bytes = io.BytesIO(files.file.read()).read()
        result = ocr_reader.readtext(image_bytes)
        return {"saved_filename": files.filename, "result": str(result)}


@app.get("/upload")
async def main():

    content = """
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
            }
            
            form {
                margin-top: 20px;
            }
            
            input[type="file"] {
                display: none;
            }
            
            .file-upload {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                cursor: pointer;
                border-radius: 4px;
                transition-duration: 0.4s;
            }
            
            .file-upload:hover {
                background-color: #45a049;
            }

            .message {
                margin-top: 20px;
            }

        </style>
    </head>
    <body>
        <h1>名片上傳</h1>
        <form action="/easyocr" enctype="multipart/form-data" method="post">
            <label for="files" class="file-upload">選擇檔案</label>
            <input id="files" name="files" type="file" multiple>
            <input type="submit" value="上傳">
        </form>
        <div id="message" class="message"></div>

        <script>
            const form = document.getElementById("uploadForm");
            const submitBtn = document.getElementById("submitBtn");
            const message = document.getElementById("message");

            form.addEventListener("submit", function(event) {
                event.preventDefault();

                submitBtn.disabled = true;
                message.textContent = "正在上傳檔案...";

                const formData = new FormData(form);

                fetch(form.action, {
                    method: form.method,
                    body: formData
                })
                .then(response => {
                    if (response.ok) {
                        message.textContent = "檔案已成功上傳！";
                    } else {
                        message.textContent = "上傳檔案時發生錯誤。";
                    }
                })
                .catch(error => {
                    message.textContent = "上傳檔案時發生錯誤：" + error.message;
                })
            });
        </script>

    </body>
    """

    return HTMLResponse(content=content)

if __name__ == "__main__":
    uvicorn.run(app, port=8000)