import os
import time
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
import uvicorn
import pypdf

app = FastAPI(title='Chat-PDF')

upload_dir = './uploads'
os.makedirs(upload_dir, exist_ok=True)

# This dictionary will store the status of each file
file_db = {}

def process_pdf(file_id: str, file_path: str):
    """
    This function runs in the background after the file is uploaded.
    """
    print(f"--- BACKGROUND TASK STARTED for file_id: {file_id} ---")
    
    try:
        # Update status to reading
        file_db[file_id]["status"] = "reading"
        print(f"Status updated to 'reading' for {file_id}")

        # Read the PDF
        reader = pypdf.PdfReader(file_path)
        total_page = len(reader.pages)
        
        # Simulate processing time
        time.sleep(3)  

        # Mark as ready
        file_db[file_id]['status'] = 'ready'
        file_db[file_id]['message'] = f"Successfully processed {total_page} pages."
        print(f"Status updated to 'ready' for {file_id}")

    except Exception as e:
        file_db[file_id]['status'] = 'failed'
        file_db[file_id]['message'] = f"Error: {e}"
        print(f"Status updated to 'failed' for {file_id}. Error: {e}")

@app.post("/upload")
async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a pdf")
    
    # 1. Generate unique ID and path INSIDE the function
    file_id = str(uuid.uuid4())
    file_path = os.path.join(upload_dir, f"{file_id}.pdf")
    
    # 2. Save file to disk
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # 3. CRITICAL: Initialize the dictionary using file_id as the KEY
    print(f"--- UPLOAD ENDPOINT: Saving to file_db with key: {file_id} ---")
    file_db[file_id] = {
        "filename": file.filename,
        "status": "processing",
        "message": "File saved. Starting background task..."
    }

    # 4. Trigger the background task
    background_tasks.add_task(process_pdf, file_id, file_path)

    return {"file_id": file_id, "message": "File uploaded successfully. Processing started."}

@app.get("/status/{file_id}")
async def get_status(file_id: str):
    print(f"--- STATUS CHECK requested for file_id: {file_id} ---")
    
    if file_id not in file_db:
        print(f"ERROR: file_id {file_id} NOT FOUND in file_db. Available keys: {list(file_db.keys())}")
        raise HTTPException(status_code=404, detail="File ID not found.")

    return {
        "file_id": file_id,
        "filename": file_db[file_id]["filename"],
        "status": file_db[file_id]["status"],
        "message": file_db[file_id].get("message", "")
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)