import whisper
from fastapi import FastAPI, UploadFile, File
import shutil
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify ["http://127.0.0.1:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# load once when app starts
whisper_model = whisper.load_model("base")  # use "base" first (faster & smaller)

@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    file_path = f"uploaded_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = whisper_model.transcribe(file_path)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "input": result["text"],
        "response": result["text"]
    }