
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

import pdfplumber
from collections import Counter
import tempfile
from fpdf import FPDF

app = FastAPI()

# ------------------ CORS ------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ HOME ------------------

@app.get("/")
def home():
    return {"message": "CareerForge Pro Running"}

# ------------------ PDF TEXT EXTRACTION ------------------

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

    stopwords = {
        "the",
        "is",
        "and",
        "in",
        "of",
        "to",
        "with",
        "a"
    }

    words = jd.lower().split()

    filtered = [
        w for w in words
        if w not in stopwords
    ]

    return Counter(filtered).most_common(10)

# ------------------ ATS SCORE ------------------

def ats_score(resume, keywords):

    resume_words = set(
        resume.lower().split()
    )

    jd_words = set([
        k[0] for k in keywords
    ])

    if len(jd_words) == 0:
        return 0

    match = (
        resume_words & jd_words
    )

    return round(
        len(match) /
        len(jd_words) * 100,
        2
    )

# ------------------ IMPROVE RESUME ------------------






def improve_resume(resume, keywords):

    key_text = ", ".join([
        k[0] for k in keywords
    ])

    suggestions = f"""
Resume Improvement Suggestions

1. Add missing technical skills:
{key_text}

2. Include more project descriptions with measurable achievements.

3. Mention technologies like:
- FastAPI
- React
- SQL
- Machine Learning

4. Add certifications and internship experience.

5. Improve ATS formatting using clear headings and bullet points.

6. Add GitHub and LinkedIn profile links.

7. Include action verbs like:
Developed, Built, Implemented, Optimized.

"""

    return suggestions



# ------------------ PDF GENERATION ------------------

def generate_pdf(text):

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font(
        "Arial",
        size=12
    )

    for line in text.split("\n"):

        pdf.cell(
            200,
            10,
            txt=line,
            ln=True
        )

    path = "output_resume.pdf"

    pdf.output(path)

    return path

# ------------------ UPLOAD API ------------------

@app.post("/upload/")
async def upload(
    file: UploadFile = File(...)
):

    text = extract_text(file)

    return {
        "resume": text
    }

# ------------------ ANALYZE API ------------------

@app.post("/analyze/")
async def analyze(data: dict):

    resume = data.get(
        "resume",
        ""
    )

    jd = data.get(
        "jd",
        ""
    )

    keywords = extract_keywords(jd)

    score = ats_score(
        resume,
        keywords
    )

    improved = improve_resume(
        resume,
        keywords
    )

    pdf_path = generate_pdf(
        improved
    )

    return {
        "keywords": keywords,
        "ats_score": score,
        "improved_resume": improved,
        "pdf_file": pdf_path
    }

# ------------------ DOWNLOAD PDF ------------------

@app.get("/download/")
def download_resume():

    return FileResponse(
        "output_resume.pdf",
        media_type="application/pdf",
        filename="improved_resume.pdf"
    )

