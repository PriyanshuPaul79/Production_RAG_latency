import os
from time import time
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(title='Chat-PDF')

upload_dir = './uploads'
os.makedirs(upload_dir,exist_ok=True)

file_db = {}

def process_pdf(file_path):
   """
   This function runs in the background after the file is uploaded.
    It handles the heavy lifting so the user doesn't have to wait.
   """

   try:
       file_db[file_id]["status"] = "processing"

       reader = pypdf.PdfReader(file_path)
       total_page = len(reader.pages)

    time.sleep(5)  # Simulate processing time
   
       file_db[file_id]["status"] = "completed"
        file
       


@app.post("/upload")
async def upload_pdf(file: UploadFile=File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code= 400, details="Please upload a pdf")
    
    file_id = str(uuid.uuid4())
    file_path = os.path.join(upload_dir,f"{file_id}.pdf")

    with open(file_path,"wb") as buffer:
        buffer.write(await file.read())

    file_db[file_path] = {
        "filename": file.filename,
        "status": "processing"
    }

    return {"file_id":file_id, "message":"File uploaded successfully"}

@app.get("/status/{file_id}")
async def get_status(file_id:str):
    if file_id not in file_db:
        raise HTTPException(status_code=404, detail="File ID not found.")

    return {
        "file_id": file_id,
        "filename":file_db[file_id]["filename"],
        "status": file_db[file_id]["status"]
    }

if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0", port=8000)