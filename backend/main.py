from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
from langchain.chat_models import ChatOpenAI

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

llm = ChatOpenAI(model_name="gpt-4")  # replace with your preferred model

# Read PDF
def read_pdf(file):
    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# Generate question from text
def generate_question(chunk):
    prompt = f"""
You are a university professor. Based on the following course material, generate a challenging question and provide the model answer:
\"\"\"{chunk}\"\"\"
Return as JSON: {{ "question": "...", "model_answer": "..." }}
"""
    response = llm.call_as_llm(prompt)
    return response  # parse JSON if needed

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile):
    text = read_pdf(file.file)
    # For simplicity, use first 500 characters
    chunk = text[:500]
    question = generate_question(chunk)
    return {"question": question}

@app.post("/check_answer/")
async def check_answer(student_answer: str = Form(...), model_answer: str = Form(...)):
    # LLM evaluates answer similarity
    prompt = f"""
Model answer: "{model_answer}"
Student answer: "{student_answer}"
Score the student's answer 0-5 and provide short feedback.
Return as JSON: {{ "score": ..., "feedback": "..." }}
"""
    result = llm.call_as_llm(prompt)
    return {"result": result}