from fastapi import APIRouter,UploadFile,File,HTTPException,status
from . import config
import logging 
from werkzeug.utils import secure_filename
import io
import os
import shutil

indexing_router = APIRouter()
 
UPLOAD_DIR = os.makedirs(config.storage_folder,exist_ok=True)

async def upload(file:UploadFile)->None:
    content = await file.read()
    stream = io.BytesIO(content)
    server_file_path = os.path.join(UPLOAD_DIR,file.filename)
    
    try:
        with open(server_file_path,"wb") as buffer:
            shutil.copyfile(file.file,buffer)
    except Exception as e:
        print(f"Error Occured : {e}")
    finally :
        await file.close()

@indexing_router("index_document")
def index_document(file : UploadFile = File(...)):
    if file.content_type not in config.ALLOWED_FILE_TYPES:
        logging.error("pls provide either image, pdf or document")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="pls provide either image, pdf or document")
    file_name = file.filename
    if file_name == secure_filename(file_name):
        logging.error("use proper file names")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="use proper file names")
    upload(file)
    