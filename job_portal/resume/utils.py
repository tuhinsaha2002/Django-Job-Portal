import re
from PyPDF2 import PdfReader
from docx import Document

# Keywords for ATS scoring
KEYWORDS = ["Python", "Django", "kotlin","AWS",]

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    reader = PdfReader(pdf_path)
    text = "".join(page.extract_text() for page in reader.pages)
    return text

def extract_text_from_docx(docx_path):
    """Extracts text from a DOCX file."""
    doc = Document(docx_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text

def calculate_ats_score(resume_file, job_description=''):
    """
    Calculates the ATS score for a resume.
    If a job description is provided, it uses the job description for keywords.
    """
    # Get the file extension
    file_name = resume_file.name
    file_extension = file_name.split('.')[-1].lower()

    # Extract text based on file type
    if file_extension == "pdf":
        text = extract_text_from_pdf(resume_file)
    elif file_extension in ["docx", "doc"]:
        text = extract_text_from_docx(resume_file)
    else:
        raise ValueError("Unsupported file format. Please upload a PDF or DOCX file.")

    # Preprocess text: Lowercase and remove special characters
    clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', text.lower())

    # Determine keywords (case insensitive)
    if job_description:
        clean_job_description = re.sub(r'[^a-zA-Z0-9\s]', '', job_description.lower())
        keywords = {keyword.strip().lower() for keyword in clean_job_description.split()}
    else:
        keywords = {keyword.lower() for keyword in KEYWORDS}

    # Count keyword matches
    total_keywords = len(keywords)
    matched_keywords = sum(1 for keyword in keywords if keyword in clean_text)

    # Calculate ATS score
    ats_score = (matched_keywords / total_keywords) * 100 if total_keywords > 0 else 0
    return round(ats_score, 2)
