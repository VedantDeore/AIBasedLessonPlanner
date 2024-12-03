from flask import Flask, render_template, request
import spacy
from datetime import datetime
import PyPDF2

app = Flask(__name__)

# Load spaCy's English model
nlp = spacy.load("en_core_web_sm")

# Function to extract text from the PDF file
def extract_pdf_text(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to extract dates and categorize events (Start of Sem, Mid Sem, End Sem)
def extract_dates_and_events(text):
    doc = nlp(text)
    semester_data = {
        "semester_start": None,
        "mid_sem": [],
        "end_sem": [],
        "semester_end": None
    }
    holidays = []
    
    # Extracting specific dates for semester, mid-sem, end-sem
    for sentence in doc.sents:
        sentence_text = sentence.text.strip()
        
        if "Start of Semester" in sentence_text:
            semester_data["semester_start"] = extract_date(sentence_text)
        
        if "Mid Semester" in sentence_text:
            semester_data["mid_sem"] = extract_date_range(sentence_text)
        
        if "End Semester Examination" in sentence_text:
            semester_data["end_sem"] = extract_date_range(sentence_text)
        
        if "Start of Semester-II" in sentence_text:
            semester_data["semester_end"] = extract_date(sentence_text)
    
    # Extracting holidays (unchanged)
    for line in text.splitlines():
        if "•" in line:  # Holidays are listed with bullet points
            holiday_info = line.split("–")
            if len(holiday_info) == 2:
                holidays.append({"holiday": holiday_info[0].replace("•", "").strip(), "date": holiday_info[1].strip()})
    
    return semester_data, holidays

# Function to extract single date
def extract_date(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "DATE":
            try:
                return datetime.strptime(ent.text, "%d/%m/%y").date()
            except ValueError:
                continue
    return None

# Function to extract date ranges
def extract_date_range(text):
    doc = nlp(text)
    dates = []
    for ent in doc.ents:
        if ent.label_ == "DATE":
            try:
                dates.append(datetime.strptime(ent.text, "%d/%m/%y").date())
            except ValueError:
                continue
    return dates if len(dates) == 2 else []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Handling PDF upload
        file = request.files["file"]
        if file:
            # Extract text from uploaded PDF
            text = extract_pdf_text(file)

            # Extract dates and events from text
            semester_data, holidays = extract_dates_and_events(text)

            return render_template("aca.html", semester_data=semester_data, holidays=holidays)
    
    return render_template("aca.html")

if __name__ == "__main__":
    app.run(debug=True)
