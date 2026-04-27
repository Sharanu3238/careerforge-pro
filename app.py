from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
from collections import Counter
import tempfile
from fpdf import FPDF

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "CareerForge Pro Running"}

# ------------------ PDF TEXT ------------------
def extract_text(upload_file):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(upload_file.file.read())
        path = tmp.name

    with pdfplumber.open(path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""

    return text

# ------------------ KEYWORDS ------------------
def extract_keywords(jd):
    stopwords = {"the","is","and","in","of","to","with","a"}
    words = jd.lower().split()
    filtered = [w for w in words if w not in stopwords]
    return Counter(filtered).most_common(10)

# ------------------ ATS ------------------
def ats_score(resume, keywords):
    resume_words = set(resume.lower().split())
    jd_words = set([k[0] for k in keywords])

    if len(jd_words) == 0:
        return 0

    match = resume_words & jd_words
    return round(len(match) / len(jd_words) * 100, 2)

# ------------------ IMPROVE ------------------
def improve_resume(resume, keywords):
    key_text = ", ".join([k[0] for k in keywords])
    return f"{resume}\n\nAdd these keywords:\n{key_text}"

# ------------------ PDF GENERATE ------------------
def generate_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in text.split("\n"):
        pdf.cell(200, 10, txt=line, ln=True)

    path = "output_resume.pdf"
    pdf.output(path)
    return path

# ------------------ APIs ------------------

@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    text = extract_text(file)
    return {"resume": text}

@app.post("/analyze/")
async def analyze(data: dict):
    resume = data.get("resume", "")
    jd = data.get("jd", "")

    keywords = extract_keywords(jd)
    score = ats_score(resume, keywords)
    improved = improve_resume(resume, keywords)

    pdf_path = generate_pdf(improved)

    return {
        "keywords": keywords,
        "ats_score": score,
        "improved_resume": improved,
        "pdf_file": pdf_path
    }