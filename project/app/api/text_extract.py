from fastapi import APIRouter, HTTPException, BackgroundTasks, File, UploadFile
from typing import Optional, List
import time
import os

from app.domain import ocr
from app.domain import fileUpload
from app.model.TextSchema import TextExtractDocument as ted
router = APIRouter()

@router.post("/extract_text")
async def extract_text(Images_in: List[UploadFile] = File(...)) -> ted:
    response = {}
    s = time.time()
    image_name = ""
    for img in Images_in:
        print("Images Uploaded: ", img.filename)
        temp_file = fileUpload._save_file_to_server(img, path="./images/", save_as=img.filename)
        text = await ocr.read_image(temp_file)
        response[img.filename] = text
        image_name = img.filename
        os.remove(temp_file)
    response["Time Taken"] = round((time.time() - s),2)
    image_out = ted(file_name=image_name, text = text, time_taken = response["Time Taken"])
    return image_out