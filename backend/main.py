from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
import os
import openai

# New OpenAI client
client = openai.OpenAI(api_key="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")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def read_pdf(file: UploadFile):
    """Extract text from a single PDF file."""
    reader = PdfReader(file.file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


@app.post("/upload_pdf/")
async def upload_pdf(files: list[UploadFile] = File(...)):
    """Generate a question from multiple PDFs using OpenAI 1.x client."""
    if not files:
        return {"error": "No PDF files uploaded."}

    full_text = ""
    for file in files:
        full_text += read_pdf(file) + "\n\n"

    truncated_text = full_text[:12000]

    prompt = f"""
You are a university professor. Read the course material below and generate **one oral exam question**.

COURSE MATERIAL:
------
{truncated_text}
------

Return JSON with:
- "question": exam question text
- "model_answer": ideal answer (3–6 sentences)
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.2
    )

    # New interface: use response.choices[0].message.content
    text = response.choices[0].message.content
    return {"question": text}


@app.post("/check_answer/")
async def check_answer(
    student_answer: str = Form(...),
    model_answer: str = Form(...)
):
    """Score a student answer using OpenAI 1.x client."""
    prompt = f"""
You are grading a student's oral exam response.

MODEL ANSWER:
{model_answer}

STUDENT ANSWER:
{student_answer}

Return JSON with:
- "score": number from 0 to 10
- "feedback": short explanation
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.2
    )

    text = response.choices[0].message.content
    return {"result": text}
