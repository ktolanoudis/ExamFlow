from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import openai
from typing import List
import io

# OpenAI client (correct way)
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Get absolute path to the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def read_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {"error": f"File not found at {index_path}"}

@app.post("/upload_pdf/")
async def upload_pdf(files: List[UploadFile] = File(...)):
    """Generate a question from multiple PDFs using ChatGPT-4."""
    if not files:
        return {"error": "No PDF files uploaded."}

    full_text = ""

    for file in files:
        contents = await file.read()
        reader = PdfReader(io.BytesIO(contents))

        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    prompt = f"""
You are a university professor. Read the course material below and generate **one highly relevant oral exam question**.

COURSE MATERIAL:
------
{full_text}
------

Return JSON with EXACTLY:
{{
  "question": "<exam question>",
  "model_answer": "<3-6 sentence ideal answer based only on the material provided>"
}}
"""

    response = client.chat.completions.create(
        model="gpt-5-mini",  # ChatGPT 4-level model
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.choices[0].message.content
    return {"question": text}


@app.post("/check_answer/")
async def check_answer(
    student_answer: str = Form(...),
    model_answer: str = Form(...)
):
    prompt = f"""
    You are grading a student's exam response using the Swiss university grading system.

    Use ONLY the following grades:
    1.0, 1.25, 1.5, 1.75,
    2.0, 2.25, 2.5, 2.75,
    3.0, 3.25, 3.5, 3.75,
    4.0, 4.25, 4.5, 4.75,
    5.0, 5.25, 5.5, 5.75, 6.0

    Grade guideline:
    6.0 = Perfect understanding, precise terminology
    5.5 = Very strong, minor omissions
    5.0 = Good understanding, slight flaws
    4.0 = Passable, some conceptual gaps
    <4.0 = Insufficient understanding
    - Always select one of the allowed grades. Do NOT invent other numbers.

    Return JSON only with EXACT keys:
    {{
      "Grade": <one of the valid grades above>,
      "feedback": "Short explanation (2-4 sentences) focusing on correctness, depth, and clarity."
    }}

    MODEL ANSWER:
    {model_answer}

    STUDENT ANSWER:
    {student_answer}
    """

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.choices[0].message.content

    return {"result": text}