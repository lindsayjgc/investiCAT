from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import pdfplumber, docx
from openai import OpenAI
import os

app = FastAPI()

# Read OpenAI API key from environment (recommended). If missing, raise a clear error.
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY environment variable is not set. Please add it to your .env or environment before starting the server."
    )

client = OpenAI(api_key=OPENAI_API_KEY)

# Serve the frontend
@app.get("/")
def home():
    return FileResponse("python_backend/templates/index.html")

@app.post("/process")
async def process(file: UploadFile = File(...)):
    text = ""
    if file.filename.endswith(".pdf"):
        with pdfplumber.open(file.file) as pdf:
            text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
    elif file.filename.endswith(".docx"):
        doc = docx.Document(file.file)
        text = "\n".join([para.text for para in doc.paragraphs])

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are given a document of information and possibly an occurrence. You will extract the following data from this document: the EVENT that occurred, the DATE or WHEN that event occurred, the LOCATION of that occurrence, and any ENTITY that participated in the event. Please structure this nicely. We plan to organize this data as a knowledge graph. \"Event\" OCCURRED_ON \"Date\", \"Event\" OCCURRED_AT \"Location\", \"Entity\" PARTICIPATES_IN \"EVENT\". And the input \"Document\" MENTIONS \"Entity\" and \"Document\" MENTIONS \"Event\"."},
            {"role": "user", "content": text},
        ],
    )
    return {"summary": response.choices[0].message.content}